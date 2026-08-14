package net.minecraft.server.jsonrpc.internalapi;

import java.util.stream.Stream;
import net.minecraft.server.jsonrpc.methods.ClientInfo;
import net.minecraft.server.jsonrpc.methods.GameRulesService;
import net.minecraft.world.level.gamerules.GameRule;

public interface MinecraftGameRuleService {
    <T> GameRulesService.GameRuleUpdate<T> updateGameRule(GameRulesService.GameRuleUpdate<T> p_451145_, ClientInfo p_429774_);

    <T> T getRuleValue(GameRule<T> p_460528_);

    <T> GameRulesService.GameRuleUpdate<T> getTypedRule(GameRule<T> p_457653_, T p_453670_);

    Stream<GameRule<?>> getAvailableGameRules();
}
