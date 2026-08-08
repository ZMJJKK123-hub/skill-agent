package com.mojang.text2speech;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public interface Narrator {
    Logger LOGGER = LoggerFactory.getLogger(Narrator.class);

    void say(final String msg, final boolean interrupt, final float volume);

    void clear();

    default boolean active() {
        return true;
    }

    void destroy();

    Narrator EMPTY = new Narrator() {
        @Override
        public void say(String msg, boolean interrupt, float volume) {
        }

        @Override
        public void clear() {
        }

        @Override
        public boolean active() {
            return false;
        }

        @Override
        public void destroy() {
        }
    };

    static Narrator getNarrator() {
        try {
            return switch (OperatingSystem.get()) {
                case LINUX -> new NarratorLinux();
                case WINDOWS -> new NarratorWindows();
                case MAC_OS -> new NarratorMac();
                default -> throw new InitializeException("Unsupported platform " + System.getProperty("os.name"));
            };
        } catch (final FatalException e) {
            throw e;
        } catch (final Throwable e) {
            LOGGER.error("Error while loading the narrator", e);
            return EMPTY;
        }
    }

    class InitializeException extends Exception {
        public InitializeException(final String message, final Throwable cause) {
            super(message, cause);
        }

        public InitializeException(final String message) {
            super(message);
        }
    }

    class FatalException extends RuntimeException {
        public FatalException(final String message) {
            super(message);
        }
    }
}
