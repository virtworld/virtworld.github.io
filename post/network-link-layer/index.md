> 本文是对链路层的总结笔记。主要参考数目为**TCP/IP Illustrated: Volume I: The Protocols**的第二章。

# **概述**

Link Layer的目的是为上层的IP协议、ARP协议和RARP协议提供服务。TCP/IP支持很多不同的链路层，包括Ethernet、token ring等。本文主要讨论Ethernet帧格式以及Maximum Transmission Unit(MTU)。

<!--more-->

# **Ethernet Frames**

{{% figure class="center" src="/images/link-layer/ethernet_encap.png"  alt="IEEE 802.2/802.3 封装(RFC1042)和Ethernet封装(RFC894)" title="IEEE 802.2/802.3 封装(RFC1042)和Ethernet封装(RFC894)"  %}}

0. 在上图Ethernet头部之前（没有画出），还有8字节的Preamble部分。这部分不属于Ethernet头部。Preamble由两部分组成：
    - 7字节(56位)的1和0交错的序列, 10101010 10101010 10101010 10101010 10101010 10101010 10101010。用于使设备和Ethernet报文的时钟同步。
	- 1字节(8位)的SFD标记，10101011。用于指示Preamble的结束，后面紧跟目标端MAC地址。
1. Ethernet头部前两部分是48位的目标硬件地址和源硬件地址。ARP和RARP协议负责将48位的硬件地址与32位的IP地址建立映射关系。
2. 之后两个字节用于识别该帧的数据类型，比如IP协议为0800。
    {{% figure class="center" src="/images/link-layer/frame-type.png"  alt="Ethernet frame type" title="Ethernet frame type"  %}}
3. 之后是数据部分，数据部分的大小必须在46字节到1500字节之间，不足46字节的需要补足。
4. 最后是4位的CRC，用于校验。

# **MTU**

MTU表示的链路层中单个帧最大传输数据量。如果上层协议需要数据报过大，会被执行分段(fragmentation)，以符合链路层协议的MTU限制。比如IP协议的fragmentation如下，具体细节在IP协议相关文章中讨论：

{{% figure class="center" src="/images/link-layer/ip-fragmentation.png"  alt="IP分段" title="IP分段"  %}}

可以使用`netstat -in`来查看MTU。