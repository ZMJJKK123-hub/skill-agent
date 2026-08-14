/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package cpw.mods.jarhandling.impl;

import java.security.CodeSigner;
import java.util.Locale;
import java.util.Map;
import java.util.jar.JarInputStream;

import net.minecraftforge.unsafe.UnsafeFieldAccess;
import net.minecraftforge.unsafe.UnsafeHacks;

public class SecureJarVerifier {
    private static final char[] LOOKUP = "0123456789abcdef".toCharArray();
    public static String toHexString(final byte[] bytes) {
        final var buffer = new StringBuffer(2*bytes.length);
        for (int i = 0, bytesLength = bytes.length; i < bytesLength; i++) {
            final int aByte = bytes[i] &0xff;
            buffer.append(LOOKUP[(aByte&0xf0)>>4]);
            buffer.append(LOOKUP[aByte&0xf]);
        }
        return buffer.toString();
    }

    //https://docs.oracle.com/en/java/javase/16/docs/specs/jar/jar.html#signed-jar-file
    public static boolean isSigningRelated(String path) {
        String filename = path.toLowerCase(Locale.ENGLISH);
        if (!filename.startsWith("meta-inf/")) // Must be in META-INF directory
            return false;
        filename = filename.substring(9);
        if (filename.indexOf('/') != -1)  // Can't be a sub-directory
            return false;
        if ("manifest.mf".equals(filename) || // Main manifest, which has the file hashes
            filename.endsWith(".sf") ||       // Signature file, which has hashes of the entries in the manifest file
            filename.endsWith(".dsa") ||      // PKCS7 signature, DSA
            filename.endsWith(".rsa"))        // PKCS7 signature, SHA-256 + RSA
            return true;

        if (!filename.startsWith("sig-")) // Unspecifed signature format
            return false;

        int ext = filename.lastIndexOf('.');
        if (ext == -1) // No extension, aparently is ok
            return true;
        if (ext < filename.length() - 4) // Only 1-3 character {-4 because we're at the . char}
            return false;
        for (int x = ext + 1; x < filename.length(); x++) {
            char c = filename.charAt(x);
            if ((c < 'a' || c > 'z') && (c < '0' || c > '9')) // Must be alphanumeric
                return false;
        }
        return true;
    }

    @Deprecated(forRemoval = true)
    public static Object getJarVerifier(Object inst) { return getJarVerifier((JarInputStream)inst); }
    public static Object getJarVerifier(JarInputStream inst) { return jarVerifier.get(inst); }
    public static boolean isParsingMeta(Object inst) { return parsingMeta.getBoolean(inst); }
    public static boolean hasSignatures(Object inst) { return anyToVerify.getBoolean(inst); }
    public static Map<String, CodeSigner[]> getVerifiedSigners(Object inst){ return verifiedSigners.get(inst); }
    public static Map<String, CodeSigner[]> getPendingSigners(Object inst){ return sigFileSigners.get(inst); }

    private static final Class<Object> JV_TYPE = getJVType();

    @SuppressWarnings("unchecked")
	private static Class<Object> getJVType() {
        try {
            return (Class<Object>)JarInputStream.class.getDeclaredField("jv").getType();
        } catch (Exception e) {
            throw new RuntimeException("Unable to get JarInputStream's jv field, this should never be possible," +
                    " be sure to report this will exact details on what JVM you're running.", e);
        }
    }

    private static final UnsafeFieldAccess<JarInputStream, Object> jarVerifier = UnsafeHacks.findField(JarInputStream.class, "jv");
    private static final UnsafeFieldAccess<Object, Map<String, CodeSigner[]>> sigFileSigners = UnsafeHacks.findField(JV_TYPE, "sigFileSigners");
    private static final UnsafeFieldAccess<Object, Map<String, CodeSigner[]>> verifiedSigners = UnsafeHacks.findField(JV_TYPE, "verifiedSigners");
    private static final UnsafeFieldAccess.Bool<Object> parsingMeta = UnsafeHacks.findBooleanField(JV_TYPE, "parsingMeta");
    private static final UnsafeFieldAccess.Bool<Object> anyToVerify = UnsafeHacks.findBooleanField(JV_TYPE, "anyToVerify");
}
