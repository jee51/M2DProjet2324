
def extend(position, array, look, threshold):
    # This function extend the from the Arguments position to the left and right
    # to find the cruise phase
    left_pos,right_pos = position, position
    # Search left position
    # l = 0
    while True:
        avg_left = np.mean(array[left_pos - look:left_pos])
        relative_dif = np.abs(avg_left - array[left_pos]/array[left_pos])
        if relative_dif < threshold:
            left_pos -= look #translate to the left
        else: #check the next 3 interval to see the trend
            next_five_mean = [np.mean(array[left_pos - (i+1)*look : left_pos - i*look]) for i in range(3)] 
            next_rel_dif = [np.abs(next_five_mean[i] - array[left_pos - i*look]/array[left_pos - i*look]) for i in range(3)]
            if np.mean(next_rel_dif) < threshold:
                left_pos -= look//10
            else:
                # print(l)
                break
        # l+=1
    # r = 0
    # Search right position
    while True:
        avg_right = np.mean(array[right_pos : right_pos+look])
        relative_dif = np.abs(avg_right - array[right_pos]/array[right_pos])
        if relative_dif < threshold:
            right_pos += look #translate to the right
        else: #check the next 3 interval to see the trend
            next_five_mean = [np.mean(array[right_pos + i*look : right_pos + (i+1)*look]) for i in range(3)] 
            next_rel_dif = [np.abs(next_five_mean[i] - array[right_pos + i*look])/array[right_pos + i*look] for i in range(3)]
            if np.mean(next_rel_dif) < threshold:
                right_pos += look//10
            else:
                # print(r)
                break
        # r+=1
    return left_pos, right_pos