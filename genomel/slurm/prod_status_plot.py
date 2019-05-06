import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf
from matplotlib.lines import Line2D
from datetime import datetime, timedelta
import postgres.utils
import postgres.status

def get_number(num, lst):
    total = len(lst)
    if num > total:
        return lst[-1]
    return lst[-1] - lst[-num]

def get_poly1d(y, x):
    fit = np.polyfit(y, x, deg=1)
    p1d = np.poly1d(fit)
    return p1d

psql_conf = '/mnt/nfs/reference/postgres_config'
engine = postgres.utils.get_db_engine(psql_conf)
prod_time, \
    nchunk_total, \
        nchunk_passed, \
            nchunk_failed, \
                indiv_pass_time, \
                    indiv_fail_time, \
                        indiv_pass_mem, \
                            indiv_fail_mem = postgres.status.get_metrics(
                                engine,
                                'pdc_freebayes_prod_metrics'
                            )
prod_time_in_hr = prod_time
prod_time_in_d = [x/24.0 for x in prod_time]
pass_persent = [round(x*100/173405.0, 2) for x in nchunk_passed]
left_persent = [round((173405-x)*100/173405.0, 2) for x in nchunk_passed]
pass_p1d = get_poly1d(prod_time, nchunk_passed)
expect_pass_hr = (173405 - pass_p1d[0])/float(pass_p1d[1])
expect_fails = 173405 * nchunk_failed[-1] / nchunk_total[-1]
fail_avg_time = np.mean(indiv_fail_time)
fail_avg_mem = np.mean(indiv_fail_mem)
total_fail = expect_fails * fail_avg_time/16/int(120/fail_avg_mem)
expect_total_hr = expect_pass_hr + 48 + total_fail
#job started at 2019-05-04T01:30:25
expect_date = datetime(2019, 5, 4, 1, 30, 25) + timedelta(hours=expect_total_hr)
table_data = np.array(
    [
        ['Expected jobs', str(173405)],
        ['Finished jobs', str(len(indiv_pass_time))],
        ['Left jobs', str(173405 - nchunk_total[-1])],
        ['Complete Percentage', str(round(len(indiv_pass_time) * 100 /float(173405), 2)) + '%'],
        ['Up time', str(round(prod_time[-1], 2)) + 'hr'],
        ['Expected days on current run', str(round(expect_pass_hr/24.0, 2))],
        ['Expected days on completion', str(round(expect_total_hr/24.0, 2))],
        ['Expected date on completion', '{:%D  %H:%M:%S}'.format(expect_date)],
        ['Last 2hr', str(get_number(3, nchunk_passed))],
        ['Last 8hr', str(get_number(9, nchunk_passed))],
        ['Last 24hr', str(get_number(25, nchunk_passed))],
        ['Last 3d', str(get_number(73, nchunk_passed))],
        ['Last 7d', str(get_number(169, nchunk_passed))]
    ]
)

pdf = pdf.PdfPages("../prod_status/bionimbus_pdc_freebayes_production_status.pdf")
fig = plt.figure(figsize=(10, 30), dpi=800)

#1st table
axis1 = fig.add_subplot(511)
collabel=("Items", "GenoMEL-Bionimbus-PDC freebayes production")
axis1.axis('tight')
axis1.axis('off')
t1 = axis1.table(
    cellText=table_data,
    colLabels=collabel,
    loc='center',
    rowLoc='center',
    colLoc='center',
    cellLoc='center',
    fontsize=12
)
t1.scale(1,3)
plt.title('GenoMEL-Bionimbus-PDC Freebayes Production Status', y=2.0)
plt.subplots_adjust(hspace=1)

#2nd plot
axis2 = fig.add_subplot(512)
passed2 = axis2.scatter(prod_time_in_d, pass_persent, color='g', s=4, marker='D')
poly2 = get_poly1d(prod_time_in_d, pass_persent)
x = (100 - poly2[0])/float(poly2[1])
dots2 =[0, x]
plt.plot(dots2, poly2(dots2), 'g--', markersize=1)
left2 = axis2.scatter(prod_time_in_d, left_persent, color='b', s=4, marker='D')
poly3 = get_poly1d(prod_time_in_d, left_persent)
y = (0 - poly3[0])/float(poly3[1])
dots3 = [0, y]
plt.plot(dots3, poly3(dots3), 'b--', markersize=1)

plt.text(x - 8, 70, 'Estimated: {} d'.format(round(x, 2)))
plt.axvline(x, color='black',lw=0.5,ls=':')
plt.axhline(100, color='black', lw=0.5, ls=':')
plt.xlabel('Days')
plt.ylabel('Percentage (%)')
plt.title("Estimated complete time on current run",fontsize=14)
custom_lines = [Line2D([0], [0], color='green', lw=4),
                Line2D([0], [0], color='blue', lw=4)]
plt.legend(custom_lines,('Finished','Left'),
        loc='best',fontsize=11, markerscale=4)

#3th plot
axis4 = fig.add_subplot(513)
passed4 = axis4.scatter(prod_time, nchunk_passed, color='g',s=6, marker='D')
failed4 = axis4.scatter(prod_time, nchunk_failed, color='r',s=6)
p_s = get_poly1d(prod_time, nchunk_passed)
plt.plot(prod_time,p_s(prod_time),"g--")
p_f = get_poly1d(prod_time, nchunk_failed)
plt.plot(prod_time,p_f(prod_time),"r--")
plt.xlabel('Hours')
plt.ylabel('Number of exonic region chunk')
plt.title("Passed and failed processes of current run",fontsize=14)
custom_lines = [Line2D([0], [0], color='green', lw=4),
                Line2D([0], [0], color='red', lw=4)]
plt.legend(custom_lines,('Passed chunks','Failed chunks'),
        loc='upper left',fontsize=11, markerscale=4)

#4th plot
axis5 = fig.add_subplot(514)
job_time = indiv_pass_time + indiv_fail_time
job_type = ['Passed chunks'] * len(indiv_pass_time) + ['Failed chunks'] * len(indiv_fail_time)
df = pd.DataFrame(list(zip(job_time, job_type)), columns =['Individual_process_time(hr)', 'Process_status'])
my_pal = {"Passed chunks": "g", "Failed chunks": "r"}
ax = sns.violinplot(x="Process_status", y="Individual_process_time(hr)", data=df, palette=my_pal)
ax.set_title('Individual chunk processed time', fontsize=14)
# Calculate number of obs per group & median to position labels
medians = df.groupby(['Process_status'])['Individual_process_time(hr)'].median().values
nobs = df['Process_status'].value_counts().values
nobs = [str(x) for x in nobs.tolist()]
nobs = ["n=" + i for i in nobs]
 # Add it to the plot
pos = range(len(nobs))
for tick,label in zip(pos,ax.get_xticklabels()):
   ax.text(pos[tick], medians[tick] + 0.03, nobs[tick], horizontalalignment='center', size='medium', color='black', weight='semibold')

#5th plot
axis6 = fig.add_subplot(515)
job_mem = indiv_pass_mem + indiv_fail_mem
job_type2 = ['Passed chunks'] * len(indiv_pass_mem) + ['Failed chunks'] * len(indiv_fail_mem)
df2 = pd.DataFrame(list(zip(job_mem, job_type2)), columns =['Individual_process_mem(GB)', 'Process_status'])
my_pal2 = {"Passed chunks": "g", "Failed chunks": "r"}
ax2 = sns.violinplot(x="Process_status", y="Individual_process_mem(GB)", data=df2, palette=my_pal2)
ax2.set_title('Individual chunk processed mem', fontsize=14)
# Calculate number of obs per group & median to position labels
medians2 = df2.groupby(['Process_status'])['Individual_process_mem(GB)'].median().values
nobs2 = df2['Process_status'].value_counts().values
nobs2 = [str(x) for x in nobs2.tolist()]
nobs2 = ["n=" + i for i in nobs2]
 # Add it to the plot
pos2 = range(len(nobs2))
for tick,label in zip(pos2,ax2.get_xticklabels()):
   ax2.text(pos[tick], medians[tick] + 0.03, nobs2[tick], horizontalalignment='center', size='medium', color='black', weight='semibold')

pdf.savefig(fig)
pdf.close()