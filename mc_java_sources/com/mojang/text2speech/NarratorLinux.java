package com.mojang.text2speech;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import com.sun.jna.Native;
import com.sun.jna.NativeLibrary;
import com.sun.jna.Pointer;

import java.util.Arrays;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public class NarratorLinux implements Narrator {
    private final AtomicInteger executionBatch = new AtomicInteger();
    private final Pointer voiceCmuUsKal16;
    private final ExecutorService executor;

    public NarratorLinux() throws InitializeException {
        FliteLibrary.loadNative();
        FliteLibrary.CmuUsKal16.loadNative();

        final int rc = FliteLibrary.flite_init();
        if (rc != FliteLibrary.SUCCESS) {
            throw new InitializeException(FliteLibrary.NATIVE_LIBRARY_NAME + " returned code " + rc);
        }

        voiceCmuUsKal16 = FliteLibrary.CmuUsKal16.register_cmu_us_kal16(null);
        if (voiceCmuUsKal16 == Pointer.NULL) {
            throw new InitializeException(FliteLibrary.CmuUsKal16.NATIVE_LIBRARY_NAME + " failed to register");
        }

        executor = Executors.newSingleThreadExecutor(new ThreadFactoryBuilder().setNameFormat("Narrator #%d").setDaemon(true).build());
    }

    @Override
    public void say(final String msg, final boolean interrupt, final float volume) {
        if (interrupt) {
            clear();
        }

        final int thisBatch = executionBatch.get();

        // Split the message by punctuations that create a pause (commas, periods, parenthesis, quotes, etc)
        Arrays.stream(msg.split("[,.:;/\"()\\[\\]{}!?\\\\]+"))
            .filter(x -> !x.isBlank())
            .forEach(unit -> executor.submit(() -> {
                if (thisBatch < executionBatch.get()) {
                    return;
                }
                final Pointer utterance = FliteLibrary.flite_synth_text(unit, voiceCmuUsKal16);
                try {
                    final Pointer wave = FliteLibrary.utt_wave(utterance);
                    if (volume != 1.0f) {
                        final int volumeFactor = (int) (volume * 65536);
                        FliteLibrary.cst_wave_rescale(wave, volumeFactor);
                    }
                    FliteLibrary.play_wave(wave);
                } finally {
                    FliteLibrary.delete_utterance(utterance);
                }
            }));
    }

    @Override
    public void clear() {
        executionBatch.incrementAndGet();
    }

    @Override
    public void destroy() {
        executor.shutdownNow();
    }

    private static class FliteLibrary {
        private static final int SUCCESS = 0;
        private static final String NATIVE_LIBRARY_NAME = "flite";

        public static void loadNative() throws InitializeException {
            try {
                Native.register(FliteLibrary.class, NativeLibrary.getInstance(NATIVE_LIBRARY_NAME));
            } catch (final Throwable e) {
                throw new InitializeException("Failed to load library " + NATIVE_LIBRARY_NAME, e);
            }
        }

        private static native int flite_init();

        private static native Pointer flite_synth_text(String text, Pointer voice);

        private static native Pointer utt_wave(Pointer utterance);

        private static native void play_wave(Pointer wave);

        private static native void cst_wave_rescale(Pointer wave, int factor);

        private static native void delete_utterance(Pointer utterance);

        private static class CmuUsKal16 {
            private static final String NATIVE_LIBRARY_NAME = "flite_cmu_us_kal16";

            public static void loadNative() throws InitializeException {
                try {
                    Native.register(CmuUsKal16.class, NativeLibrary.getInstance(NATIVE_LIBRARY_NAME));
                } catch (final Throwable e) {
                    throw new InitializeException("Failed to load library " + NATIVE_LIBRARY_NAME, e);
                }
            }

            private static native Pointer register_cmu_us_kal16(final String voxdir);
        }
    }
}
