/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package cpw.mods.cl;

import java.io.IOException;
import java.io.InputStream;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.function.Function;

/**
 * UnionFileSystem implements this as a base Java provider normally now.
 */
@Deprecated(forRemoval = true)
public class UnionURLStreamHandler implements ModularURLHandler.IURLProvider {
    @Override
    public String protocol() {
        return "union";
    }

    @Override
    public Function<URL, InputStream> inputStreamFunction() {
        return u -> {
            try {
                var path = Paths.get(u.toURI());
                return Files.newInputStream(path);
            } catch (URISyntaxException | IOException e) {
                return sneak(e);
            }
        };
    }


    @SuppressWarnings("unchecked")
    private static <E extends Throwable, R> R sneak(Exception exception) throws E {
        throw (E)exception;
    }
}
