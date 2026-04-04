"""
公共层冒烟测试。

验证 src/common/ 的基础类型和接口可正常导入和使用。
"""
from common.models import DamageType, EntityId, Position, StatBlock
from common.interfaces import GameEngine, EventBus


class TestPosition:
    def test_distance_to_same_point(self):
        p = Position(x=0, y=0)
        assert p.distance_to(p) == 0.0

    def test_distance_to_other(self):
        a = Position(x=0, y=0)
        b = Position(x=3, y=4)
        assert a.distance_to(b) == 5.0


class TestStatBlock:
    def test_is_alive(self):
        s = StatBlock(hp=10, max_hp=100)
        assert s.is_alive is True

    def test_is_dead(self):
        s = StatBlock(hp=0, max_hp=100)
        assert s.is_alive is False

    def test_take_damage_returns_new_object(self):
        s = StatBlock(hp=50, max_hp=100, defense=10)
        damaged = s.take_damage(20)
        assert damaged.hp == 30
        assert s.hp == 50  # 原对象不变

    def test_take_damage_clamps_to_zero(self):
        s = StatBlock(hp=10, max_hp=100)
        damaged = s.take_damage(999)
        assert damaged.hp == 0

    def test_heal_clamps_to_max(self):
        s = StatBlock(hp=50, max_hp=100)
        healed = s.heal(999)
        assert healed.hp == 100


class TestDamageType:
    def test_enum_values(self):
        assert DamageType.PHYSICAL == "physical"
        assert DamageType.TRUE == "true"
