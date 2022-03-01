import os

disp_size = (960, 480)

for file in os.listdir('Final/selected_labels'):
    fpath = os.path.join('Final/selected_labels', file)
    npath = os.path.join('wrongFinal', file)
    
    lines = []
    changed = 0

    with open(fpath, 'r') as infile:
        for line in infile.read().split('\n'):
            if len(line) == 0: 
                continue
            c, x, y, w, h = line.split(' ')
            x,y,w,h = float(x),float(y),float(w),float(h)

            x1 = x - w/2
            x2 = x + w/2
            y1 = y - h/2
            y2 = y + h/2

            if any([val < 0 or val > 1 for val in [x1, x2, y1, y2]]):
                changed = 1
                if x1 < 0:
                    diff = abs(x1)
                    x+= diff/2
                    w-= diff
                if y1 < 0:
                    diff = abs(y1)
                    y+= diff/2
                    h-= diff

                if x2 > 1:
                    diff=x2-1
                    x-= diff/2
                    w-= diff
                if y2 > 1:
                    diff=y2-1
                    y-= diff/2
                    h-= diff

                x1 = x - w/2
                x2 = x + w/2
                y1 = y - h/2
                y2 = y + h/2

                assert all([not (val < 0 or val > 1) for val in [x1, x2, y1, y2]])

            lines.append("{} {} {} {} {}".format(c,x,y,w,h))

        if changed:
            with open(npath, 'w') as outfile:
                outfile.write('\n'.join(lines))


