'''
f = open("/proc/nstat", "rb")
c = f.read(128 * 4)

for i in range(128):
    j = 4*i
    print(str(c[j]) + "." + str(c[j+1]) + "." + str(c[j+2]) + "." + str(c[j+3]))

f.close()
'''

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

init_country_ips()

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

            print("s_ip = " + s_ip + "\nb_ip = " + b_ip)

            r = s_ip + "," + b_ip
            if(country_ips.__contains__(r)):
                return country_ips[r]
    return "unknown"


print(get_ip_country("8.8.8.8"))
