package net.minecraft.server.network;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import io.netty.channel.Channel;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.IoHandlerFactory;
import io.netty.channel.MultiThreadIoEventLoopGroup;
import io.netty.channel.ServerChannel;
import io.netty.channel.epoll.Epoll;
import io.netty.channel.epoll.EpollIoHandler;
import io.netty.channel.epoll.EpollServerSocketChannel;
import io.netty.channel.epoll.EpollSocketChannel;
import io.netty.channel.kqueue.KQueue;
import io.netty.channel.kqueue.KQueueIoHandler;
import io.netty.channel.kqueue.KQueueServerSocketChannel;
import io.netty.channel.kqueue.KQueueSocketChannel;
import io.netty.channel.local.LocalChannel;
import io.netty.channel.local.LocalIoHandler;
import io.netty.channel.local.LocalServerChannel;
import io.netty.channel.nio.NioIoHandler;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.channel.socket.nio.NioSocketChannel;
import java.util.concurrent.ThreadFactory;
import org.jspecify.annotations.Nullable;

public abstract class EventLoopGroupHolder {
    private static final EventLoopGroupHolder NIO = new EventLoopGroupHolder("NIO", NioSocketChannel.class, NioServerSocketChannel.class) {
        @Override
        protected IoHandlerFactory ioHandlerFactory() {
            return NioIoHandler.newFactory();
        }
    };
    private static final EventLoopGroupHolder EPOLL = new EventLoopGroupHolder("Epoll", EpollSocketChannel.class, EpollServerSocketChannel.class) {
        @Override
        protected IoHandlerFactory ioHandlerFactory() {
            return EpollIoHandler.newFactory();
        }
    };
    private static final EventLoopGroupHolder KQUEUE = new EventLoopGroupHolder("Kqueue", KQueueSocketChannel.class, KQueueServerSocketChannel.class) {
        @Override
        protected IoHandlerFactory ioHandlerFactory() {
            return KQueueIoHandler.newFactory();
        }
    };
    private static final EventLoopGroupHolder LOCAL = new EventLoopGroupHolder("Local", LocalChannel.class, LocalServerChannel.class) {
        @Override
        protected IoHandlerFactory ioHandlerFactory() {
            return LocalIoHandler.newFactory();
        }
    };
    private final String type;
    private final Class<? extends Channel> channelCls;
    private final Class<? extends ServerChannel> serverChannelCls;
    private volatile @Nullable EventLoopGroup group;
    private volatile @Nullable EventLoopGroup groupClient;

    public static EventLoopGroupHolder remote(boolean p_453425_) {
        if (p_453425_) {
            if (KQueue.isAvailable()) {
                return KQUEUE;
            }

            if (Epoll.isAvailable()) {
                return EPOLL;
            }
        }

        return NIO;
    }

    public static EventLoopGroupHolder local() {
        return LOCAL;
    }

    EventLoopGroupHolder(String p_451976_, Class<? extends Channel> p_460581_, Class<? extends ServerChannel> p_455144_) {
        this.type = p_451976_;
        this.channelCls = p_460581_;
        this.serverChannelCls = p_455144_;
    }

    private ThreadFactory createThreadFactory(boolean client) {
        return new ThreadFactoryBuilder().setNameFormat("Netty " + this.type + (client ? " Client" : " Server") + " IO #%d").setDaemon(true).setThreadFactory(net.minecraftforge.fml.util.thread.SidedThreadGroups.get(client)).build();
    }

    protected abstract IoHandlerFactory ioHandlerFactory();

    private EventLoopGroup createEventLoopGroup(boolean client) {
        return new MultiThreadIoEventLoopGroup(this.createThreadFactory(client), this.ioHandlerFactory());
    }

    public EventLoopGroup eventLoopGroup() {
        return eventLoopGroup(false);
    }

    public EventLoopGroup eventLoopGroup(boolean client) {
        EventLoopGroup eventloopgroup = client ? this.groupClient : this.group;
        if (eventloopgroup == null) {
            synchronized (this) {
                eventloopgroup = client ? this.groupClient : this.group;
                if (eventloopgroup == null) {
                    eventloopgroup = this.createEventLoopGroup(client);
                    if (client)
                        this.groupClient = eventloopgroup;
                    else
                        this.group = eventloopgroup;
                }
            }
        }

        return eventloopgroup;
    }

    public Class<? extends Channel> channelCls() {
        return this.channelCls;
    }

    public Class<? extends ServerChannel> serverChannelCls() {
        return this.serverChannelCls;
    }
}
