package com.mojang.blocklist;

import javax.annotation.Nullable;
import java.util.function.Predicate;

public interface BlockListSupplier {
    @Nullable
    Predicate<String> createBlockList();
}
