package net.minecraft.server.commands;

import com.mojang.brigadier.exceptions.CommandSyntaxException;

@FunctionalInterface
public interface InCommandFunction<T, R> {
    R apply(T p_395002_) throws CommandSyntaxException;
}
