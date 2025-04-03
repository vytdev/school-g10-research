"""
Copyright (c) 2025  Vincent Yanzee J. Tan
For my research paper. Fortunately, I'm good at coding, and math.
"""

import random
import math
import csv

SAMPLE_SIZE = 235
SIMULATED_ASSESSMENT_QUIZ_ITEMS = 50


# We'll use normally distributed random numbers to simulate
# real world data. (note: This is all a simulation and may not
# directly reflect real-world results)
#
# Why don't just use a simple random generator? We used box
# muller to get a normally distributed random float. What
# does this mean? By normally distributed, it means that the
# generated scores will be focused on the mean (0 in this case).
# This ensures consistency throughout reinvocations of the
# simulation.
def box_muller():
    """
    Generate a pair of normally distributed random numbers
    from uniformly distributed random numbers.
    """

    u1 = random.random()  # Uniform(0,1)
    u2 = random.random()  # Uniform(0,1)
    
    # Box-Muller transformation
    z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    z1 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)
    
    return z0, z1  # Two independent standard normal variables


# Another layer to ensure maximum data correctness. Takes
# an initial estimate for the standard deviation.
def gen_variable_procedural(initialStdDev):
    """
    Generate a variable procedural result. This is to make sure
    that there will be no biasing in the resulting simulated
    scores.
    """

    z0, z1 = box_muller()  # Generate normally distributed score

    # Use a sigmoid transformation to smoothly map
    # (-inf, inf) to (0, 1). 0.5 will be the median.
    clamped_z0 = 1 / (1 + math.exp(-z0))

    # Use z0 as the standard normal variable.
    return clamped_z0 * initialStdDev


# Final layer to ensure that the students'/learners' score
# will approximately reflect real-world results. The
# inverseBiasingFactor must be a number between [-1.0, 1.0]
def gen_simulated_learner_score(inverseBiasingFactor):
    """
    Get the simulated students' score. This will `approximately`
    reflect the real world results. Though, actual real results
    may vary depending on the population count and the finalized
    sample size.
    """

    # Why 20? to ensure fairness in the probabilistic
    # distribution. This gives us the normal range.
    initial_std_dev = 20

    # The extreme scores. In reality, we'll hardly get
    # high scores nor very low scores. This eliminates
    # that.
    extremes = SIMULATED_ASSESSMENT_QUIZ_ITEMS - initial_std_dev

    # This gives us the median starting and ending point.
    # This is where the weighted scores will start.
    median_half_terminal = extremes / 2

    # Generate the variable procedural result.
    proc = gen_variable_procedural(initial_std_dev)

    # This will normalise the scores. How the inverseBiasingFactor
    # affects the final score? Negative values will reduce the
    # generated score. Positive values will increase the generated
    # score. It must be between [-1.0, 1.0]
    alpha = inverseBiasingFactor * median_half_terminal

    # Round off to the lower integer. We don't get decimals in
    # real-world scores!! This step is necessary.
    return math.floor(median_half_terminal + alpha + proc)

# Setup a csv file for our results.
fd = open("scores.csv", mode="w")
writer = csv.writer(fd)

writer.writerow([
    "student ref id",
    "pre-quiz score",
    "post-quiz score",
    "score difference"
])

# The pre-quiz total, post-quiz total, and diff total.
# Set to zero initially. These scores will accumulate
# after the simulation phase.
preTotal  = 0
postTotal = 0
diffTotal = 0
diffList  = []    # Collect the diffs

# Generate 235 simulated scores.
for i in range(0, SAMPLE_SIZE):
    # Increase the inverse biasing factor in the post-quiz
    # score by 45%. Simulates real-world impact.
    preQuiz  = gen_simulated_learner_score(0.15)
    postQuiz = gen_simulated_learner_score(0.60)
    diff = postQuiz - preQuiz

    writer.writerow([ i, preQuiz, postQuiz, diff ])

    # Accumulate to the totals.
    preTotal  += preQuiz
    postTotal += postQuiz
    diffTotal += diff
    diffList.append(diff)


# Compute for the mean.
preMean  = preTotal  / SAMPLE_SIZE
postMean = postTotal / SAMPLE_SIZE
diffMean = diffTotal / SAMPLE_SIZE

sumSqDiff = sum((x - diffMean) ** 2 for x in diffList)
diffsVariance = sumSqDiff / (SAMPLE_SIZE - 1)
diffStdDev = math.sqrt(diffsVariance)

stdError = diffStdDev / math.sqrt(SAMPLE_SIZE)
pairedTTest = diffMean / stdError

cohensD = diffMean / diffStdDev

print("sample size:      ", SAMPLE_SIZE)
print("sim quiz items:   ", SIMULATED_ASSESSMENT_QUIZ_ITEMS)
print("RESULTS:")
print("pre-quiz mean:    ", preMean)
print("post-quiz mean:   ", postMean)
print("FOR PAIRED T-TEST AND COHEN'S D ANALYSIS:")
print("difference mean:  ", diffMean)
print("diff std dev:     ", diffStdDev)
print("ANALYSIS VALUES:")
print("t-statistic:      ", pairedTTest)
print("cohen's d:        ", cohensD)

# Save the csv file.
fd.close()
