/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package cpw.mods.niofs.union;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.net.URISyntaxException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLStreamHandler;
import java.net.spi.URLStreamHandlerProvider;
import java.nio.file.Paths;


public class UnionURLStreamHandlerProvider extends URLStreamHandlerProvider {
    @Override
    public URLStreamHandler createURLStreamHandler(String protocol) {
        if ("union".equals(protocol)) {
            return new URLStreamHandler() {
                @Override
                protected URLConnection openConnection(URL url) throws IOException {
                    return new URLConnection(url) {
                        @Override public void connect() throws IOException {}

                        @Override
                        public InputStream getInputStream() throws IOException {
                            try {
                                if (Paths.get(this.url.toURI()) instanceof UnionPath upath)
                                    return upath.buildInputStream();
                                throw new IllegalArgumentException("Invalid Path " + this.url.toURI());
                            } catch (URISyntaxException e) {
                                return sneak(e);
                            } catch (UncheckedIOException e) {
                                throw e.getCause();
                            }
                        }
                    };
                }
            };
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    private static <E extends Throwable, R> R sneak(Exception exception) throws E {
        throw (E)exception;
    }
}
