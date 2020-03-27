
    # calculating days to double the total cases
    days_to_double = [0] * time_delta.days 
    for i, total in enumerate(totals):
        j = i - 1
        days_to_double[i] = 0
        while j > 0:
            if totals[j] <= 0.5 * totals[i]:
                days_to_double[i] = i - j
                break
            j -= 1

    # calculating percentage change in over three days
    percent_change = [0] * time_delta.days 
    for i, total in enumerate(totals):
        if i >= 3:
            percent_change[i] = total / totals[i-3]
        else:
            percent_change[i] = 0

