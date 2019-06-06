
import matplotlib.pyplot as plt

def plot_schedule(schedule):
    task_profiles = {task.id:schedule.task_resource_usage[0][task.id] for task in schedule.tasks_scheduled}
    fig, ax = plt.subplots()
    resource_usage = {}
    blocks = {}
    for task_id in task_profiles:
        blocks[task_id] = []
        block_start = 0
        block_q = 0
        last_q = 0
        for t in range(len(task_profiles[task_id])):
            current_q = task_profiles[task_id][t]
            if current_q != last_q:
                blocks[task_id].append((block_start, t-block_start, block_q))
                if current_q == 0:
                    break
                block_start = t
                block_q = current_q
                last_q = current_q
        print('%d: ' %task_id, blocks[task_id])
        # removing trivial first block
        blocks[task_id] = blocks[task_id][1:]
        color = ['blue', 'green', 'red', 'yellow', 'pink', 'black', 'orange', 'purple', 'brown', 'gray'][task_id] 
        for block in blocks[task_id]:
            start = block[0]
            duration = block[1]
            finish = start + duration
            q = block[2]
            ax.broken_barh([(start, duration)], (0, q), color = color, edgecolor = 'none', alpha = 0.3)
            ax.text(start + duration/2, q/2, '%d' %task_id, color='black')
            # updating resource usage
            try:
                resource_usage[start] += q
            except:
                resource_usage[start] = q
            try: 
                resource_usage[finish] += -q
            except:
                resource_usage[finish] = -q
    # getting overall resource usage
    resource_usage = dict(sorted(resource_usage.items()))
    cumsum = 0
    for time in resource_usage:
        cumsum += resource_usage[time]
        resource_usage[time] =  cumsum
    # adding resource usage as step function
    ax.step([x for x in resource_usage.keys()], [y for y in resource_usage.values()], where = 'post')
    
    ax.set_xlim(0, max(resource_usage.keys())+5)
    ax.set_ylim(0, max(resource_usage.values())+2)
    ax.set_xlabel('time')
    ax.set_ylabel('resource usage')
    ax.set_xticks(range(0,max(resource_usage.keys())+5,2))
    
    plt.savefig('myexampleschedule.png')




