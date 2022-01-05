fIn = open('bag_uit.xyz','r')
fOut = open ('bag_uit_clip.xyz','w')
i = 0
print('Start script')
for row in fIn:
    if str(row.split()[2]) != '1000000.0':
        fOut.write(row)
        i = i + 1
        if i % 100000 == 0:
            print(i)
            if i == 20000000:
                break
fIn.close()
fOut.close()
print('End script')
