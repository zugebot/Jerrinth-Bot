# Jerrin Shirks

# native imports

# custom imports
from files.jerrinth import JerrinthBot
from files.wrappers import *
from files.config import *
from files.support import *
import time


class UGBCBlock:
    def __init__(self, _id: str, _name: str, _weight: int) -> None:
        self.id: str = _id
        self.name: str = _name
        self.weight: int = _weight


class FindBlockCog(commands.Cog):

    def __init__(self, bot):
        self.bot: JerrinthBot = bot

        self.__block_list = [
            'acacia_button:16',
            'acacia_door:32',
            'acacia_fence_gate:16',
            'acacia_pressure_plate:16',
            'acacia_stairs:8',
            'acacia_standing_sign:16',
            'acacia_trapdoor:16',
            'acacia_wall_sign:8',
            'activator_rail:16',
            'air:1',
            'andesite_stairs:8',
            'anvil:16',
            'bamboo:16',
            'bamboo_sapling:16',
            'barrel:16',
            'barrier:1',
            'beacon:1',
            'bed:16',
            'bedrock:2',
            'beetroot:8',
            'bell:32',
            'birch_button:16',
            'birch_door:32',
            'birch_fence_gate:16',
            'birch_pressure_plate:16',
            'birch_stairs:8',
            'birch_standing_sign:16',
            'birch_trapdoor:16',
            'birch_wall_sign:8',
            'black_glazed_terracotta:8',
            'blast_furnace:8',
            'blue_glazed_terracotta:8',
            'blue_ice:1',
            'bone_block:16',
            'bookshelf:1',
            'brewing_stand:8',
            'brick_block:1',
            'brick_stairs:8',
            'brown_glazed_terracotta:8',
            'brown_mushroom:1',
            'brown_mushroom_block:16',
            'bubble_column:2',
            'cactus:16',
            'cake:8',
            'campfire:8',
            'carpet:16',
            'carrots:8',
            'cartography_table:1',
            'carved_pumpkin:4',
            'cauldron:16',
            'chain_command_block:16',
            'chemical_heat:1',
            'chemistry_table:16',
            'chest:8',
            'chorus_flower:8',
            'chorus_plant:1',
            'clay:1',
            'coal_block:1',
            'coal_ore:1',
            'cobblestone:1',
            'cobblestone_wall:16',
            'cocoa:16',
            'colored_torch_bp:16',
            'colored_torch_rg:16',
            'command_block:16',
            'composter:16',
            'concrete:16',
            'concretePowder:16',
            'conduit:1',
            'coral:8',
            'coral_block:16',
            'coral_fan:16',
            'coral_fan_dead:16',
            'coral_fan_hang:16',
            'coral_fan_hang2:16',
            'coral_fan_hang3:16',
            'crafting_table:1',
            'cyan_glazed_terracotta:8',
            'dark_oak_button:16',
            'dark_oak_door:32',
            'dark_oak_fence_gate:16',
            'dark_oak_pressure_plate:16',
            'dark_oak_stairs:8',
            'dark_oak_trapdoor:16',
            'dark_prismarine_stairs:8',
            'darkoak_standing_sign:16',
            'darkoak_wall_sign:8',
            'daylight_detector:16',
            'daylight_detector_inverted:16',
            'deadbush:1',
            'detector_rail:16',
            'diamond_block:1',
            'diamond_ore:1',
            'diorite_stairs:8',
            'dirt:2',
            'dispenser:16',
            'double_plant:16',
            'double_stone_slab:16',
            'double_stone_slab2:16',
            'double_stone_slab3:16',
            'double_stone_slab4:16',
            'double_wooden_slab:16',
            'dragon_egg:1',
            'dried_kelp_block:1',
            'dropper:16',
            'element_0:1',
            'element_1:1',
            'element_10:1',
            'element_100:1',
            'element_101:1',
            'element_102:1',
            'element_103:1',
            'element_104:1',
            'element_105:1',
            'element_106:1',
            'element_107:1',
            'element_108:1',
            'element_109:1',
            'element_11:1',
            'element_110:1',
            'element_111:1',
            'element_112:1',
            'element_113:1',
            'element_114:1',
            'element_115:1',
            'element_116:1',
            'element_117:1',
            'element_118:1',
            'element_12:1',
            'element_13:1',
            'element_14:1',
            'element_15:1',
            'element_16:1',
            'element_17:1',
            'element_18:1',
            'element_19:1',
            'element_2:1',
            'element_20:1',
            'element_21:1',
            'element_22:1',
            'element_23:1',
            'element_24:1',
            'element_25:1',
            'element_26:1',
            'element_27:1',
            'element_28:1',
            'element_29:1',
            'element_3:1',
            'element_30:1',
            'element_31:1',
            'element_32:1',
            'element_33:1',
            'element_34:1',
            'element_35:1',
            'element_36:1',
            'element_37:1',
            'element_38:1',
            'element_39:1',
            'element_4:1',
            'element_40:1',
            'element_41:1',
            'element_42:1',
            'element_43:1',
            'element_44:1',
            'element_45:1',
            'element_46:1',
            'element_47:1',
            'element_48:1',
            'element_49:1',
            'element_5:1',
            'element_50:1',
            'element_51:1',
            'element_52:1',
            'element_53:1',
            'element_54:1',
            'element_55:1',
            'element_56:1',
            'element_57:1',
            'element_58:1',
            'element_59:1',
            'element_6:1',
            'element_60:1',
            'element_61:1',
            'element_62:1',
            'element_63:1',
            'element_64:1',
            'element_65:1',
            'element_66:1',
            'element_67:1',
            'element_68:1',
            'element_69:1',
            'element_7:1',
            'element_70:1',
            'element_71:1',
            'element_72:1',
            'element_73:1',
            'element_74:1',
            'element_75:1',
            'element_76:1',
            'element_77:1',
            'element_78:1',
            'element_79:1',
            'element_8:1',
            'element_80:1',
            'element_81:1',
            'element_82:1',
            'element_83:1',
            'element_84:1',
            'element_85:1',
            'element_86:1',
            'element_87:1',
            'element_88:1',
            'element_89:1',
            'element_9:1',
            'element_90:1',
            'element_91:1',
            'element_92:1',
            'element_93:1',
            'element_94:1',
            'element_95:1',
            'element_96:1',
            'element_97:1',
            'element_98:1',
            'element_99:1',
            'emerald_block:1',
            'emerald_ore:1',
            'enchanting_table:1',
            'end_brick_stairs:8',
            'end_bricks:1',
            'end_gateway:1',
            'end_portal:1',
            'end_portal_frame:8',
            'end_rod:8',
            'end_stone:1',
            'ender_chest:8',
            'farmland:8',
            'fence:8',
            'fence_gate:16',
            'fire:16',
            'fletching_table:1',
            'flower_pot:2',
            'flowing_lava:16',
            'flowing_water:16',
            'frame:8',
            'frosted_ice:4',
            'furnace:8',
            'glass:1',
            'glass_pane:1',
            'glowingobsidian:1',
            'glowstone:1',
            'gold_block:1',
            'gold_ore:1',
            'golden_rail:16',
            'granite_stairs:8',
            'grass:1',
            'grass_path:1',
            'gravel:1',
            'gray_glazed_terracotta:8',
            'green_glazed_terracotta:8',
            'grindstone:16',
            'hard_glass:1',
            'hard_glass_pane:1',
            'hard_stained_glass:16',
            'hard_stained_glass_pane:16',
            'hardened_clay:1',
            'hay_block:16',
            'heavy_weighted_pressure_plate:16',
            'hopper:16',
            'ice:1',
            'info_update:1',
            'info_update2:1',
            'invisibleBedrock:1',
            'iron_bars:1',
            'iron_block:1',
            'iron_door:32',
            'iron_ore:1',
            'iron_trapdoor:16',
            'jigsaw:8',
            'jukebox:1',
            'jungle_button:16',
            'jungle_door:32',
            'jungle_fence_gate:16',
            'jungle_pressure_plate:16',
            'jungle_stairs:8',
            'jungle_standing_sign:16',
            'jungle_trapdoor:16',
            'jungle_wall_sign:8',
            'kelp:16',
            'ladder:8',
            'lantern:2',
            'lapis_block:1',
            'lapis_ore:1',
            'lava:16',
            'lava_cauldron:16',
            'leaves:16',
            'leaves2:16',
            'lectern:8',
            'lever:16',
            'light_blue_glazed_terracotta:8',
            'light_weighted_pressure_plate:16',
            'lime_glazed_terracotta:8',
            'lit_blast_furnace:8',
            'lit_furnace:8',
            'lit_pumpkin:4',
            'lit_redstone_lamp:1',
            'lit_redstone_ore:1',
            'lit_smoker:8',
            'log:16',
            'log2:16',
            'loom:4',
            'magenta_glazed_terracotta:8',
            'magma:1',
            'melon_block:1',
            'melon_stem:8',
            'mob_spawner:1',
            'monster_egg:8',
            'mossy_cobblestone:1',
            'mossy_cobblestone_stairs:8',
            'mossy_stone_brick_stairs:8',
            'movingBlock:1',
            'mycelium:1',
            'nether_brick:1',
            'nether_brick_fence:1',
            'nether_brick_stairs:8',
            'nether_wart:4',
            'nether_wart_block:1',
            'netherrack:1',
            'netherreactor:1',
            'normal_stone_stairs:8',
            'noteblock:1',
            'oak_stairs:8',
            'observer:16',
            'obsidian:1',
            'orange_glazed_terracotta:8',
            'packed_ice:1',
            'pink_glazed_terracotta:8',
            'piston:8',
            'pistonArmCollision:8',
            'planks:8',
            'podzol:1',
            'polished_andesite_stairs:8',
            'polished_diorite_stairs:8',
            'polished_granite_stairs:8',
            'portal:4',
            'potatoes:8',
            'powered_comparator:16',
            'powered_repeater:16',
            'prismarine:4',
            'prismarine_bricks_stairs:8',
            'prismarine_stairs:8',
            'pumpkin:4',
            'pumpkin_stem:8',
            'purple_glazed_terracotta:8',
            'purpur_block:16',
            'purpur_stairs:8',
            'quartz_block:16',
            'quartz_ore:1',
            'quartz_stairs:8',
            'rail:16',
            'red_flower:16',
            'red_glazed_terracotta:8',
            'red_mushroom:1',
            'red_mushroom_block:16',
            'red_nether_brick:1',
            'red_nether_brick_stairs:8',
            'red_sandstone:4',
            'red_sandstone_stairs:8',
            'redstone_block:1',
            'redstone_lamp:1',
            'redstone_ore:1',
            'redstone_torch:8',
            'redstone_wire:16',
            'reeds:16',
            'repeating_command_block:16',
            'reserved6:1',
            'sand:2',
            'sandstone:4',
            'sandstone_stairs:8',
            'sapling:16',
            'scaffolding:16',
            'seaLantern:1',
            'sea_pickle:8',
            'seagrass:4',
            'shulker_box:16',
            'silver_glazed_terracotta:8',
            'skull:16',
            'slime:1',
            'smithing_table:1',
            'smoker:8',
            'smooth_quartz_stairs:8',
            'smooth_red_sandstone_stairs:8',
            'smooth_sandstone_stairs:8',
            'smooth_stone:1',
            'snow:1',
            'snow_layer:16',
            'soul_sand:1',
            'sponge:2',
            'spruce_button:16',
            'spruce_door:32',
            'spruce_fence_gate:16',
            'spruce_pressure_plate:16',
            'spruce_stairs:8',
            'spruce_standing_sign:16',
            'spruce_trapdoor:16',
            'spruce_wall_sign:8',
            'stained_glass:16',
            'stained_glass_pane:16',
            'stained_hardened_clay:16',
            'standing_banner:16',
            'standing_sign:16',
            'sticky_piston:8',
            'stone:8',
            'stone_brick_stairs:8',
            'stone_button:16',
            'stone_pressure_plate:16',
            'stone_slab:16',
            'stone_slab2:16',
            'stone_slab3:16',
            'stone_slab4:16',
            'stone_stairs:8',
            'stonebrick:8',
            'stonecutter:1',
            'stonecutter_block:8',
            'stripped_acacia_log:4',
            'stripped_birch_log:4',
            'stripped_dark_oak_log:4',
            'stripped_jungle_log:4',
            'stripped_oak_log:4',
            'stripped_spruce_log:4',
            'structure_block:8',
            'sweet_berry_bush:8',
            'tallgrass:4',
            'tnt:4',
            'torch:8',
            'trapdoor:16',
            'trapped_chest:8',
            'tripWire:16',
            'tripwire_hook:16',
            'turtle_egg:16',
            'underwater_torch:8',
            'undyed_shulker_box:1',
            'unlit_redstone_torch:8',
            'unpowered_comparator:16',
            'unpowered_repeater:16',
            'vine:16',
            'wall_banner:8',
            'wall_sign:8',
            'water:16',
            'waterlily:1',
            'web:1',
            'wheat:8',
            'white_glazed_terracotta:8',
            'wood:16',
            'wooden_button:16',
            'wooden_door:32',
            'wooden_pressure_plate:16',
            'wooden_slab:16',
            'wool:16',
            'yellow_flower:1',
            'yellow_glazed_terracotta:8',
        ]
        self.blocks: list[UGBCBlock] = []
        self.weights: list[int] = []
        for block in self.__block_list:
            _blockID, _blockWeight = block.split(":", 1)
            _blockName = " ".join([i.capitalize() for i in _blockID.split("_")])

            obj = UGBCBlock(_blockID, _blockName, int(_blockWeight))
            self.blocks.append(obj)
            self.weights.append(obj.weight)

    def getRandomBlock(self) -> UGBCBlock:
        _block = random.choices(self.blocks, self.weights)
        return _block[0]

    @wrapper_command(name="findblock", cooldown=FINDBLOCK_COOLDOWN)
    async def findBlockCommand(self, ctx: CtxObject):

        self.bot.ensureUserExists(ctx)
        if self.bot.getUser(ctx).get("findblock", None) is None:
            self.bot.getUser(ctx)["findblock"] = EMPTY_FINDBLOCK.copy()

        _block = self.getRandomBlock()
        if _block.id == "end_portal":
            self.bot.getUser(ctx)["findblock"]["end_portal_count"] += 1
        self.bot.getUser(ctx)["findblock"]["use_total"] += 1
        self.bot.getUser(ctx)["findblock"]["use_last"] = time.time()
        self.bot.saveData()

        _name, _id = _block.name, random.randint(0, _block.weight - 1)
        _insert = f" with an id of **{_id}**" if _block.weight != 1 and False else ""
        _starter = "an " if _name[0] in "aeiouAEIOU" else "a "
        if _block.id == "end_portal":
            emoji = self.bot.getEmoji("end_portal")
            _message = f"<@{ctx.author.id}> → *you found the **End Portal**!*"
            _count = self.bot.getUser(ctx)['findblock']['end_portal_count']

            _message += f"\nYou have found **{_count} {emoji}** so far!"
        else:
            _message = f"<@{ctx.author.id}> → you found {_starter}**{_name}**{_insert}."

        await ctx.send(_message, allowed_mentions=False)

    @findBlockCommand.error
    @wrapper_error(use_cooldown=True)
    async def findBlockCommandError(self, ctx, error):
        pass


async def setup(bot):
    await bot.add_cog(FindBlockCog(bot))