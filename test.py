f = open("/proc/nstat", "rb")
c = f.read(128 * 4)

for i in range(128):
    j = 4*i
    print(str(c[j]) + "." + str(c[j+1]) + "." + str(c[j+2]) + "." + str(c[j+3]))

f.close()
