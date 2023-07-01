"""Unit Tests for plogic/prop.py"""

from itertools import product
import pytest
from typing import Optional

from plogic.core import And, Atomic, Not, Proposition, Or, Implies, Iff, atomics


simple5: list[Proposition] = [
    Not(Atomic("p")),
    And(Atomic("p"), Atomic("q")),
    Or(Atomic("p"), Atomic("q")),
    Implies(Atomic("p"), Atomic("q")),
    Iff(Atomic("p"), Atomic("q")),
]
# [~p, p&q, p|q, p->q, p<->q]

simple6: list[Proposition] = [Atomic("p"), *simple5]
# [p, ~p, p&q, p|q, p->q, p<->q]


class TestPropositionCompositionMethods:
    """Tests for the five composition methods in the Proposition class."""

    @pytest.mark.parametrize("u", simple6)
    def test_invert(self, u: Proposition):
        assert u.__invert__() == Not(u)
        assert ~u == Not(u)

    binary_test_cases_with_correct_types = [
        (Atomic("p"), Atomic("q")),  # (p, q)
        *product(simple5, [Atomic("r")]),  # (~p, r), (p&q, r), ...
        *product([Atomic("r")], simple5),  # (r, ~p), (r, p&q), ...
    ]
    binary_test_cases_with_wrong_second_type = [
        *product(simple6, [object(), True, False])
    ]

    @pytest.mark.parametrize("u,v", binary_test_cases_with_correct_types)
    def test_and_correct_type(self, u: Proposition, v: Proposition):
        """Tests (u & v) where u and v are both Proposition's"""
        assert u.__and__(v) == And(u, v)
        assert u & v == And(u, v)

    @pytest.mark.parametrize("u,x", binary_test_cases_with_wrong_second_type)
    def test_and_incorrect_type(self, u: Proposition, x):
        """Tests u.__and__(x) where u is a Proposition, but x is not."""
        assert u.__and__(x) is NotImplemented

    @pytest.mark.parametrize("u,v", binary_test_cases_with_correct_types)
    def test_or_correct_type(self, u: Proposition, v: Proposition):
        """Tests (u | v) where u and v are both Proposition's"""
        assert u.__or__(v) == Or(u, v)
        assert u | v == Or(u, v)

    @pytest.mark.parametrize("u,x", binary_test_cases_with_wrong_second_type)
    def test_or_incorrect_type(self, u: Proposition, x):
        """Tests u.__or__(x) where u is a Proposition, but x is not."""
        assert u.__or__(x) is NotImplemented

    @pytest.mark.parametrize("u,v", binary_test_cases_with_correct_types)
    def test_implies(self, u: Proposition, v: Proposition):
        """Tests u.implies(v) where u and v are both Proposition's"""
        assert u.implies(v) == Implies(u, v)

    @pytest.mark.parametrize("u,v", binary_test_cases_with_correct_types)
    def test_iff(self, u: Proposition, v: Proposition):
        """Tests u.iff(v) where u and v are both Proposition's"""
        assert u.iff(v) == Iff(u, v)


class TestPropositionMiscSpecialMethods:
    @pytest.mark.parametrize("u", simple6)
    def test_bool(self, u):
        """Tests that bool(u) raises TypeError"""
        with pytest.raises(TypeError):
            bool(u)


atomic_test_cases: list[Atomic] = [
    Atomic("p"),
    Atomic("ANY_NamE"),
    Atomic(""),
    Atomic("\\'\"\n\t\uFFFF"),
]


class TestInterpretation:
    """Tests the _interpret methods in the subclasses and __call__ method of
    the Proposition class."""

    Interp = dict[str, bool]

    def interpret3(self, u: Proposition, interp: Interp) -> bool:
        """Interprets in all three ways and asserts that all values are equal,
        and then returns the value.

        The three ways:
            u(mapping)
            u(**vals)
            u._interpret(mapping)
        """
        a = u(interp)
        b = u(**interp)
        c = u._interpret(interp)
        assert a == b == c
        return a

    def expect_interpret_fail(self, u: Proposition, interp: Interp) -> None:
        """Asserts that all interpret will raise a ValueError in all three
        ways."""
        with pytest.raises(ValueError):
            u(interp)
        with pytest.raises(ValueError):
            u(**interp)
        with pytest.raises(ValueError):
            u._interpret(interp)

    @pytest.mark.parametrize("atomic", atomic_test_cases)
    def test_atomic_name_found(self, atomic: Atomic):
        """Tests Atomic._interpret"""
        assert self.interpret3(atomic, {atomic.name: True}) is True
        assert self.interpret3(atomic, {atomic.name: False}) is False

    @pytest.mark.parametrize("atomic", [Atomic("p"), Atomic("q")])
    def test_atomic_name_not_found(self, atomic: Atomic):
        """Tests Atomic._interpret"""
        self.expect_interpret_fail(atomic, {atomic.name + "2": True})
        self.expect_interpret_fail(atomic, {atomic.name + "2": False})

    def test_not_truth_table(self):
        """Tests truth table of ~p"""
        not_p = Not(Atomic("p"))
        assert self.interpret3(not_p, {"p": True}) is False
        assert self.interpret3(not_p, {"p": False}) is True

    def test_and_truth_table(self):
        """Tests truth table of p&q"""
        p_and_q = And(Atomic("p"), Atomic("q"))
        assert self.interpret3(p_and_q, {"p": True, "q": True}) is True
        assert self.interpret3(p_and_q, {"p": True, "q": False}) is False
        assert self.interpret3(p_and_q, {"p": False, "q": True}) is False
        assert self.interpret3(p_and_q, {"p": False, "q": False}) is False

    def test_or_truth_table(self):
        """Tests truth table of p|q"""
        p_or_q = Or(Atomic("p"), Atomic("q"))
        assert self.interpret3(p_or_q, {"p": True, "q": True}) is True
        assert self.interpret3(p_or_q, {"p": True, "q": False}) is True
        assert self.interpret3(p_or_q, {"p": False, "q": True}) is True
        assert self.interpret3(p_or_q, {"p": False, "q": False}) is False

    def test_implies_truth_table(self):
        """Tests truth table of p->q"""
        p_implies_q = Implies(Atomic("p"), Atomic("q"))
        assert self.interpret3(p_implies_q, {"p": True, "q": True}) is True
        assert self.interpret3(p_implies_q, {"p": True, "q": False}) is False
        assert self.interpret3(p_implies_q, {"p": False, "q": True}) is True
        assert self.interpret3(p_implies_q, {"p": False, "q": False}) is True

    def test_iff_truth_table(self):
        """Tests truth table of p<->q"""
        p_iff_q = Iff(Atomic("p"), Atomic("q"))
        assert self.interpret3(p_iff_q, {"p": True, "q": True}) is True
        assert self.interpret3(p_iff_q, {"p": True, "q": False}) is False
        assert self.interpret3(p_iff_q, {"p": False, "q": True}) is False
        assert self.interpret3(p_iff_q, {"p": False, "q": False}) is True

    @pytest.mark.parametrize(
        "u,interp_expected_pairs",
        [
            (
                Not(Not(Not(Not(Atomic("p"))))),  # ~~~~p  (quadruple negation)
                [
                    ({"p": True}, True),
                    ({"p": False}, False),
                ],
            ),
            (
                Or(Atomic("p"), Not(Atomic("p"))),  # p | ~p  (tautology)
                [
                    ({"p": True}, True),
                    ({"p": False}, True),
                ],
            ),
            (
                And(Atomic("p"), Not(Atomic("p"))),  # p & ~p  (contradiction)
                [
                    ({"p": True}, False),
                    ({"p": False}, False),
                ],
            ),
            (
                Implies(
                    And(Implies(Atomic("p"), Atomic("q")), Atomic("p")),
                    Atomic("q"),
                ),  # ((p->q)&q) -> q  (Modens Ponens, so a tautology)
                [
                    ({"p": True, "q": True}, True),
                    ({"p": True, "q": False}, True),
                    ({"p": False, "q": True}, True),
                    ({"p": False, "q": False}, True),
                ],
            ),
            (
                Iff(
                    Iff(Atomic("p"), Atomic("q")),
                    And(
                        Implies(Atomic("p"), Atomic("q")),
                        Implies(Atomic("q"), Atomic("p")),
                    ),
                ),  # (p <-> q) <-> ((p -> q) & (q -> p))  (tautology)
                [
                    ({"p": True, "q": True}, True),
                    ({"p": True, "q": False}, True),
                    ({"p": False, "q": True}, True),
                    ({"p": False, "q": False}, True),
                ],
            ),
            (
                Iff(
                    Iff(Atomic("p"), Atomic("q")),
                    Or(
                        And(Atomic("p"), Atomic("q")),
                        And(Not(Atomic("p")), Not(Atomic("q"))),
                    ),
                ),  # (p <-> q) <-> ((p & q) | (~p & ~q))  (tautology)
                [
                    ({"p": True, "q": True}, True),
                    ({"p": True, "q": False}, True),
                    ({"p": False, "q": True}, True),
                    ({"p": False, "q": False}, True),
                ],
            ),
        ],
    )
    def test_complex_cases(
        self,
        u: Proposition,
        interp_expected_pairs: list[tuple[Interp, bool]],
    ):
        """Test cases with some nesting."""
        for interp, expected in interp_expected_pairs:
            assert self.interpret3(u, interp) is expected

    @pytest.mark.parametrize(
        "u,interp_expected_pairs",
        [
            (
                And(
                    Or(
                        Implies(Atomic("p"), Atomic("p")),
                        Iff(Atomic("p"), Atomic("p")),
                    ),
                    Not(Atomic("p")),
                ),  # ((p -> p) | (p <-> p)) & ~p
                [
                    ({}, None),
                    ({"x": True}, None),
                ],
            ),
            # The following tests also try to test the "short circuiting"
            # nature of interpreting.
            (
                Not(Atomic("p")),
                [  # ~p
                    ({}, None),
                    ({"x": True}, None),
                    ({"x": False}, None),
                ],
            ),
            (
                And(Atomic("p"), Atomic("q")),  # p & q
                [
                    ({}, None),
                    ({"p": True}, None),
                    ({"p": False}, False),
                    ({"q": True}, None),
                    ({"q": False}, None),
                ],
            ),
            (
                Or(Atomic("p"), Atomic("q")),  # p | q
                [
                    ({}, None),
                    ({"p": True}, True),
                    ({"p": False}, None),
                    ({"q": True}, None),
                    ({"q": False}, None),
                ],
            ),
            (
                Implies(Atomic("p"), Atomic("q")),  # p -> q (== ~p | q)
                [
                    ({}, None),
                    ({"p": True}, None),
                    ({"p": False}, True),
                    ({"q": True}, None),
                    ({"q": False}, None),
                ],
            ),
            (
                Iff(Atomic("p"), Atomic("q")),  # p <-> q
                [
                    ({}, None),
                    ({"p": True}, None),
                    ({"p": False}, None),
                    ({"q": True}, None),
                    ({"q": False}, None),
                ],
            ),
        ],
    )
    def test_complex_atomic_missing(
        self,
        u: Proposition,
        interp_expected_pairs: list[tuple[Interp, Optional[bool]]],
    ):
        """Test cases with some nesting when an atomic value is not assigned"""
        for interp, expected in interp_expected_pairs:
            if expected is None:
                self.expect_interpret_fail(u, interp)
            else:
                assert self.interpret3(u, interp) is expected


class TestStr:
    """Test the __str__ methods of the six subclasses."""

    @pytest.mark.parametrize("atomic", atomic_test_cases)
    def test_atomic(self, atomic: Atomic):
        assert str(atomic) == atomic.name

    @pytest.mark.parametrize("atomic", atomic_test_cases)
    def test_not(self, atomic: Atomic):
        assert str(Not(atomic)) == f"~{atomic}"

    @pytest.mark.parametrize(
        "cls,conn",
        [
            (And, "&"),
            (Or, "|"),
            (Implies, "->"),
            (Iff, "<->"),
        ],
    )
    @pytest.mark.parametrize("a", atomic_test_cases[1:])
    @pytest.mark.parametrize("b", atomic_test_cases[2:])
    def test_binary_conn(self, cls: type, conn: str, a: Atomic, b: Atomic):
        assert str(cls(a, b)) == f"({a.name} {conn} {b.name})"

    @pytest.mark.parametrize(
        "u,expected",
        [
            (
                Not(Not(Not(Not(Atomic("p"))))),
                "~~~~p",
            ),
            (
                Implies(
                    And(Implies(Atomic("p"), Atomic("q")), Atomic("p")),
                    Atomic("q"),
                ),
                "(((p -> q) & p) -> q)",
            ),
            (
                Iff(
                    Iff(Atomic("p"), Atomic("q")),
                    And(
                        Implies(Atomic("p"), Atomic("q")),
                        Implies(Atomic("q"), Atomic("p")),
                    ),
                ),
                "((p <-> q) <-> ((p -> q) & (q -> p)))",
            ),
            (
                Iff(
                    Iff(Atomic("p"), Atomic("q")),
                    Or(
                        And(Atomic("p"), Atomic("q")),
                        And(Not(Atomic("p")), Not(Atomic("q"))),
                    ),
                ),
                "((p <-> q) <-> ((p & q) | (~p & ~q)))",
            ),
        ],
    )
    def test_complex(self, u: Proposition, expected: str):
        assert str(u) == expected


class TestMisc:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("", ()),
            (" \t\f\r\n", ()),
            ("P", (Atomic("P"),)),
            ("P Q R", (Atomic("P"), Atomic("Q"), Atomic("R"))),
            ("1234 %()$&", (Atomic("1234"), Atomic("%()$&"))),
            (
                "apple pear banana",
                (Atomic("apple"), Atomic("pear"), Atomic("banana")),
            ),
            (
                ("apple", "pear", "banana"),
                (Atomic("apple"), Atomic("pear"), Atomic("banana")),
            ),
            (
                ["apple", "pear", "banana", " \t\f\r\n"],
                (
                    Atomic("apple"),
                    Atomic("pear"),
                    Atomic("banana"),
                    Atomic(" \t\f\r\n"),
                ),
            ),
        ],
    )
    def test_atomics_function(self, text: str, expected: tuple[Atomic, ...]):
        assert atomics(text) == expected
