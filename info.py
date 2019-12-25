import time

freq = 2 #once in 2s read data from nstat file
ips_num = 256 #number of ips in nstat file

nstat_file = open("/proc/nstat", "rb")
country_ips_file = open("ip_ranges.csv", "r")
country_ips = {}

#init dict of ip ranges and countries
def init_country_ips():
    for line in country_ips_file:
        data = line.split(';')
        r = data[0]
        country = data[1]
        country_ips[r] = country

def get_ip_from_oct(oct):
    ip = ""
    ip += str(oct[0])
    ip += "."
    ip += str(oct[1])
    ip += "."
    ip += str(oct[2])
    ip += "."
    ip += str(oct[3])
    return ip


#every ip in dict is broadcast ip or routing prefix
#apply smaller subnets masks until we find country
#or return unknown
def get_ip_country(ip):
    oct_s = ip.split('.') #octets of smallest address in subnet
    oct_b = ip.split('.') #octets of broadcats address
    oct_s[3] = 0x00
    oct_b[3] = 0xff
    trim_m = 0xff #mask for trimming int to one byte
    for i in range(1,3):
        r_s = int(oct_s[3-i])
        r_b = int(oct_b[3-i])
        for j in range(9):
            #make mask smaller
            mask = 0xff << j

            #calculate new smallest subnet address
            r_s = r_s & mask
            oct_s[3-i] = r_s  
            
            #new broadcast address
            r_b = (r_b | (~mask)) & trim_m
            oct_b[3-i] = r_b

            s_ip = get_ip_from_oct(oct_s)
            b_ip = get_ip_from_oct(oct_b)

            r = s_ip + "," + b_ip
            if(country_ips.__contains__(r)):
                return country_ips[r]
    return "unknown"


def read_from_nstat():
    global nstat_file

    c = nstat_file.read(ips_num * 4)
    ips = []
    r = int(len(c)/4)
    for i in range(r):
        j = 4*i
        ip = str(c[j]) + "." + str(c[j+1]) + "." + str(c[j+2]) + "." + str(c[j+3])
        ips.append(ip)

    return ips


def main():
    init_country_ips()

    while 1:
        #read data from nstat file and parse it
        ips = read_from_nstat()
        for ip in ips:
            country = get_ip_country(ip)
            print(ip + " : " + country)
        time.sleep(freq)

main()
