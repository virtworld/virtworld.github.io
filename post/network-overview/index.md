> 本文是对计算机网络概述的总结笔记。主要参考数目为**TCP/IP Illustrated: Volume I: The Protocols**的第一章。

网络(通信)协议是一些列交换信息的规则（比如格式、含义等）。它提供了高层的接口，将硬件细节对应用程序员隐藏，使得不同的应用可以在不同的硬件上运行并通信。协议栈(protocol suite)指的是在不同层级上不同协议的组合，比如TCP/IP协议栈。
层级(layering)是协议栈设计的一种常用方法，每一层协议处理不同层级的抽象，并且通过一个通用的接口与高层和底层的协议通信。分层的原则是运行在层级N上的程序必须能够准确地收到同样运行在层级N上的另一台主机上的程序发送的信息。

TCP/IP协议栈一般被认为是一种四层协议系统，如下表所示。

```text
Applcation: Telnet, FTP, Email
Transport: TCP, UDP
Network: IP, ICMP, IGMP,
Link: device driver and interface card
```

这里的Application层又对应ISO七层网络模型中的上三层的(由下至上)Session, Presentation, Application；Link对应ISO中最下层的(由下至上)Physical和Link层。这里简单记录各层的作用：

1. 链路层。处理硬件接口的细节。
2. 网络层（或英特网层）。处理数据包在网络中移动的过程，比如路由。
3. 运输层。为应用层提供端到端的通信。
4. 应用层。负责处理特定应用的细节。

<!--more-->

在下图中我们可以看到两个在不同网络中的主机通过一个路由器相连。英特网的一个目标是将物理的网络结构对应用隐藏，正是这种对细节的隐藏使得英特网的概念如此强大，它可以让运行在不同网络上的无数主机通信。

{{% figure class="center" src="/images/network-protocol-overview/connection.gif" alt="通过路由连接在一起的两个网络" title="通过路由连接在一起的两个网络" %}}

上图中我们可以区分出终端系统（位于两端的主机）和中介系统（路由器）。应用层和传输层使用的是端到端协议，这两层协议也只有在两端才会用到；而网络层使用的是逐级(hop-by-hop)的协议，它会在两端以及所有中介节点上使用。

另一种链接两个网络的方式为桥接。桥接在链路层连接网络，而路由器在网络层连接网络。桥接使得多个LAN网络看上去象是一个LAN网络。TCP/IP网络一般倾向于使用路由器构建。

下图展示了TCP/IP协议栈。

{{% figure class="center" src="/images/network-protocol-overview/tcpip-layering.gif" alt="TCP/IP协议栈" title="TCP/IP协议栈" %}}

# **封装**

当应用程序通过TCP下而已发送数据的时候，数据通过TCP/IP协议栈逐级向下传递，每一层协议添加一个头部（也有尾部）信息，直到数据作为比特流发送到网络上。TCP协议发送给IP协议的信息单元为TCP报文段(segment)，IP协议发送给网络接口的信息单元为IP数据报(datagram)，通过Ethernet的比特流的信息单元为Ethernet帧(frame)。下图显示了这一逐级封装的过程。

{{% figure class="center" src="/images/network-protocol-overview/encapsulation.gif" alt="封装" title="封装" %}}




# **解除多路复用 Demultiplexing**

当一个以太网帧到达目标主机的时候，它从协议栈逐级向上传递，同时头部逐层被相应的协议移除。每个协议都从它的头部中确定到底应该由哪一种上层协议来处理这段数据。这个过程被称为解除多路复用。


{{% figure class="center" src="/images/network-protocol-overview/demultiplexing.gif" alt="解除多路复用" title="解除多路复用" %}}

`TCP/IP详解 卷一：协议`中的备注：ICMP和IGMP虽然封装在IP数据报中但是逻辑上和IP协议属于同一层；同样ARP和RARP有它们自己的Ethernet帧类型，但是它们逻辑上也属于Ethernet一层。


# **端口号**

服务器通常都有一些“知名端口号”(well-known port)，这些知名端口号由Internet Assigned Numbers Authority管理。任何TCP/IP协议的实现都提供的服务在1-1023端口号，比如FTP服务器在TCP的21端口，Telnet服务器在TCP的23端口TFTP协议在UDP的69端口。

客户端通常不在乎用什么端口，这些被称为临时端口(ephemeral ports)，它们只在客户端运行时被使用。通常TCP/IP实现将临时端口分配在1024-5000，大于5000的端口号被其他“不知名”的服务使用。

Unix系统有保留端口(reserved ports)的概念，只有有超级用户权限的进程才可以给它自己分配一个保留端口。保留端口为1-1023。
