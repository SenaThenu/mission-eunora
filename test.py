from datetime import datetime

print(datetime(2043, 1, 1, 1, 46, 40))


def flip_list(lis):
    output = []
    for i in range(1, len(lis)+1):
        output.append(lis[-i])
    return output


def add(moment):

    # Extracting...
    time_formats = []
    # minute, hour, day, month, year
    extractors = ["M", "H", "d", "m", "Y"]
    for extractor in extractors:
        time_formats.append(int(moment.strftime(f"%{extractor}")))

    giga_sec = 10**9
    # Converting the giga into ...
    secs = giga_sec % 60
    mins = (giga_sec // 60) % 60
    hours = ((giga_sec // 60) // 60) % 24
    days = ((giga_sec // 60) // 60) // 24 % 30
    months = ((giga_sec // 60) // 60) // 24 // 30 % 12
    years = ((giga_sec // 60) // 60) // 24 // 30 // 12

    for i, time in enumerate(time_formats):
        if i == 0:
            test_time = time + mins
            if test_time > 60:
                time_formats[i] = test_time - 60
                hours += 1
            else:
                time_formats[i] = test_time
        elif i == 1:
            test_time = time + hours
            if test_time > 24:
                time_formats[i] = test_time - 24
                days += 1
            else:
                time_formats[i] = test_time
        elif i == 2:
            test_time = time + days
            if test_time > 30:
                time_formats[i] = test_time - 30
                months += 1
            else:
                time_formats[i] = test_time
        elif i == 3:
            test_time = time + months
            if test_time > 12:
                time_formats[i] = test_time - 12
                months = 0
                years += 1
            else:
                time_formats[i] = test_time
        else:
            time_formats[i] += years

    final = flip_list(time_formats)

    return datetime(*final, secs)


final = add(datetime(2011, 4, 25, 0, 0))
print(final)
