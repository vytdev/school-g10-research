import scipy.stats as stats

t_stat = 18.47241222104462
df = 234

p_val = 2 * stats.t.sf(abs(t_stat), df)

print("p-val: ", p_val)
