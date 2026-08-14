package com.mojang.text2speech;

import ca.weblite.objc.Client;
import ca.weblite.objc.NSObject;
import ca.weblite.objc.Proxy;
import ca.weblite.objc.RuntimeUtils;
import ca.weblite.objc.annotations.Msg;
import com.google.common.collect.Queues;
import com.sun.jna.Pointer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Queue;

public class NarratorMac extends NSObject implements Narrator {
    private static final Logger LOGGER = LoggerFactory.getLogger(NarratorMac.class);

    private final Proxy synth = Client.getInstance().sendProxy("NSSpeechSynthesizer", "alloc");
    private final Queue<String> queue = Queues.newConcurrentLinkedQueue();
    private boolean speaking;
    private boolean crashed;

    public NarratorMac() {
        super("NSObject");
        if (Pointer.nativeValue(synth.getPeer()) == 0) {
            throw new FatalException("Failed to create `NSSpeechSynthesizer`");
        }
        if (Pointer.nativeValue(getPeer()) == 0) {
            throw new FatalException("Failed to create `NSSpeechSynthesizerDelegate`");
        }
        init();
        setDelegate();
    }

    private void init() {
        final Pointer init = RuntimeUtils.sel("init");
        if (Pointer.nativeValue(init) == 0) {
            throw new FatalException("Failed to find `init` selector");
        }
        RuntimeUtils.msg(synth.getPeer(), init);
    }

    private void setDelegate() {
        final Pointer setDelegate = RuntimeUtils.sel("setDelegate:");
        if (Pointer.nativeValue(setDelegate) == 0) {
            throw new FatalException("Failed to find `setDelegate:` selector");
        }
        RuntimeUtils.msg(synth.getPeer(), setDelegate, getPeer());
    }

    private void startSpeaking(final String message) {
        synth.send("startSpeakingString:", message);
    }

    @Msg(selector = "speechSynthesizer:didFinishSpeaking:", signature = "v@:B")
    public void didFinishSpeaking(final boolean naturally) {
        if (queue.isEmpty()) {
            speaking = false;
        } else {
            startSpeaking(queue.poll());
        }
    }

    @Override
    public void say(final String msg, final boolean interrupt, final float volume) {
        if (crashed) {
            return;
        }
        try {
            synth.send("setVolume:", volume);

            if (interrupt) {
                synth.send("stopSpeaking");
            }
            if (speaking) {
                queue.offer(msg);
            } else {
                speaking = true;
                startSpeaking(msg);
            }
        } catch (Throwable e) {
            crashed = true;
            LOGGER.error("Narrator crashed", e);
        }
    }

    @Override
    public void clear() {
        queue.clear();
        synth.send("stopSpeaking");
    }

    @Override
    public void destroy() {
    }
}
