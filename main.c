//linux kernel module
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
//netfilter, ip, tcp, udp
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>
//procfs
#include <linux/proc_fs.h>



/*
 * https://people.cs.clemson.edu/~westall/853/notes/netfilter.pdf netfilter
 * https://buffer.antifork.org/linux/procfs-guide.pdf obsolete (kernel version <= 3)
 */

#define procfs_name "nstat"
struct proc_dir_entry *nstat_ent;  //info structure of uor file in /proc

#define DATA_SZ 128
uint32_t* ips = NULL;
int ips_sz = 0;

static struct nf_hook_ops *hook_ops = NULL; //hook inf ostructure



static unsigned int hfunc(void *priv, struct sk_buff *skb, const struct nf_hook_state *state)
{
    //https://elixir.bootlin.com/linux/v4.2/source/include/linux/skbuff.h#L527
	if (!skb)
		return NF_ACCEPT;

	struct iphdr *ip_header = (struct iphdr *)skb_network_header(skb);
    uint32_t dest_ip = (uint32_t)ip_header->daddr;

	if(ips_sz == DATA_SZ){
		//stop collecting data
		return NF_ACCEPT;	
	}

	ips[ips_sz] = dest_ip;
	ips_sz += 1;
	
	return NF_ACCEPT;
}

static ssize_t nstat_write(struct file *file, const char __user *buf, size_t count, loff_t *pos) 
//__user macro tells that buf is ptr in user space (do not dereference, it might cause page fault)
{
	return -1;
}
 
static ssize_t nstat_read(struct file *file, char __user *buf, size_t count, loff_t *pos) 
{
	//only whole buffer transfer permitted

	printk("main: read\n");

	if(count < DATA_SZ * sizeof(uint32_t))
		return -1;

	copy_to_user(buf, ips, DATA_SZ * sizeof(uint32_t));
	ips_sz = 0;

	return DATA_SZ * sizeof(uint32_t);
}

static struct file_operations nstat_ops = 
{
	.owner = THIS_MODULE,
	.read = nstat_read,
	.write = nstat_write,
};

static int __init LKM_init(void)
{
	nstat_ent = proc_create(procfs_name, 0660, NULL, &nstat_ops);

	//init ip array
	if(ips == NULL)
		ips = kcalloc(1, sizeof(unsigned int) * DATA_SZ, GFP_KERNEL);
	
	
	hook_ops = (struct nf_hook_ops*)kcalloc(1, sizeof(struct nf_hook_ops), GFP_KERNEL); //allocate kernel ram
	
	// init netfilter hook
	hook_ops->hook 	= (nf_hookfn*)hfunc;		//function to be called
	hook_ops->hooknum 	= NF_INET_PRE_ROUTING;		//packets to interupt
	hook_ops->pf 	= PF_INET;			//ipv4
	hook_ops->priority 	= NF_IP_PRI_FIRST;		//hook priority
	
	nf_register_net_hook(&init_net, hook_ops);
}

static void __exit LKM_exit(void)
{
	nf_unregister_net_hook(&init_net, hook_ops);
	kfree(hook_ops);
	proc_remove(nstat_ent);
}

module_init(LKM_init);
module_exit(LKM_exit);