import pytest
from cogs.pronouns import Pronouns


@pytest.fixture
def cog(bot) -> Pronouns:
    return Pronouns(bot)


@pytest.fixture
def pronouns_list() -> list[str]:
    return ["he", "she", "ze"]


@pytest.fixture
def replacements() -> dict[str, str]:
    return {
        "$subjective_pronoun": "she",
        "$objective_pronoun": "her",
        "$possessive_pronoun": "hers",
        "$possessive_determiner": "her",
        "$reflective_pronoun": "herself",
        "$name": "Claire",
    }


def test_parse_pronouns(cog: Pronouns, pronouns_list: list[str]):
    result = cog.parse_pronouns(pronouns_list)
    assert "he/him, she/her" in result
    assert "ze" in result
    assert "he/him, she/her, ze" == result


@pytest.mark.parametrize(
    "sentence,expected",
    [
        (
            "$name is very cute! $subjective_pronoun looks stunning in a celestial dress!",
            True,
        ),
        (
            "$nammmmee is verontgubsodfus ..fs.d.fs $subjective_prononononon WHAT!",
            False,
        ),
        ("", False),
    ],
)
def test_validate(cog: Pronouns, sentence: str, expected: str):
    assert cog.validate(sentence) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("kaNAde", "Kanade"),
        ("Noelle", "Noelle"),
        ("jqCK", "Jqck"),
        ("FOSUBDFOS", "Fosubdfos"),
    ],
)
def test_convert_to_proper_name(cog: Pronouns, name: str, expected: str):
    converted = cog.convert_to_proper_name(name)
    assert converted == expected


@pytest.mark.parametrize(
    "sentence,expected",
    [
        ("this is a book", "This is a book"),
        ("THIS is a BOOK", "This is a BOOK"),
        ("WHAT DO YOU WANT!", "What DO YOU WANT!"),
    ],
)
def test_convert_to_proper_sentence(cog: Pronouns, sentence: str, expected: str):
    assert cog.convert_to_proper_sentence(sentence) == expected


@pytest.mark.parametrize(
    "sentence,expected",
    [
        (
            "$objective_pronoun name is $name. $subjective_pronoun shines as bright as the sky, and reflects $reflective_pronoun in a glittery celestial dress.",
            "her name is Claire. she shines as bright as the sky, and reflects herself in a glittery celestial dress.",
        ),
        ("$name is cute!", "Claire is cute!"),
        ("That dress is $possessive_pronoun!", "That dress is hers!"),
        ("$possessive_determiner bag is on the chair.", "her bag is on the chair."),
    ],
)
def test_parse_pronouns_sentence(
    cog: Pronouns, replacements: dict[str, str], sentence: str, expected: str
):
    assert cog.parse_pronouns_sentence(replacements, sentence) == expected


@pytest.mark.parametrize(
    "sentence,expected",
    [
        (
            "$objective_pronoun name is $name. As $subjective_pronoun twills through the fairylands, $subjective_pronoun finds a wishing well across from the fields.",
            "Her name is Claire. As she twills through the fairylands, she finds a wishing well across from the fields.",
        ),
        (
            "$subjective_pronoun saw $reflective_pronoun in the mirror, and gasped. What a stunning dress, $subjective_pronoun thought.",
            "She saw herself in the mirror, and gasped. What a stunning dress, she thought.",
        ),
    ],
)
def test_pronouns_tester(
    cog: Pronouns, replacements: dict[str, str], sentence: str, expected: str
):
    parsed_sentence = cog.parse_pronouns_sentence(replacements, sentence)
    completed_sentence = cog.convert_to_proper_sentence(parsed_sentence)
    assert completed_sentence == expected
