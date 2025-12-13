import pytest
from cogs.dictionary import Dictionary
from typing import Any, Optional


@pytest.fixture
def cog(bot) -> Dictionary:
    return Dictionary(bot)


@pytest.mark.parametrize(
    "flags,expected",
    [
        ('["Abroromantic"]', ['"Abroromantic"']),
        ('["Abrosexual"]', ['"Abrosexual"']),
        ('["Two Spirit","Two Spirit_"]', ['"Two Spirit","Two Spirit_"']),
    ],
)
def test_split_flags(cog: Dictionary, flags: str, expected: str):
    assert cog.split_flags(flags) == expected


@pytest.mark.parametrize(
    "entry,expected",
    [
        (
            {"flags": "[]", "images": "01GP3RYDBKEHR6DNCV7HWPZE2S"},
            "https://dclu0bpcdglik.cloudfront.net/images/01GP3RYDBKEHR6DNCV7HWPZE2S-flag.png",
        ),
        (
            {"flags": '["Abroromantic"]', "images": ""},
            "https://en.pronouns.page/flags/Abroromantic.png",
        ),
        (
            {
                "flags": '["Two Spirit","Two Spirit_"]',
                "images": "01FE7WPBA5YCGNY819Y9REWTXT,01FE7WQS5BCT7Z4YSWNYEWYTSP,01HMNR02Z8ACYXX52B2Y0FZH15",
            },
            "https://en.pronouns.page/flags/Two%20Spirit.png",
        ),
        (
            {
                "flags": "[]",
                "images": "01FE7WPBA5YCGNY819Y9REWTXT,01FE7WQS5BCT7Z4YSWNYEWYTSP,01HMNR02Z8ACYXX52B2Y0FZH15",
            },
            "https://dclu0bpcdglik.cloudfront.net/images/01FE7WPBA5YCGNY819Y9REWTXT-flag.png",
        ),
        ({"flags": "[]", "images": "[object Object]"}, ""),
        ({"flags": "[]", "images": ""}, ""),
    ],
)
def test_determine_image_url(cog: Dictionary, entry: dict[str, Any], expected: str):
    assert cog.determine_image_url(entry) == expected


@pytest.mark.parametrize(
    "content,expected",
    [
        (
            "a term referring to people whose {#AGAB=gender assigned at birth} is different than their {gender identity}. It includes {#trans man=trans men} and {#trans woman=trans women} as well as {non-binary} people. Many, but not all, transgender people experience {gender dysphoria} or {#gender euphoria=euphoria}",
            [
                "#AGAB=gender assigned at birth",
                "gender identity",
                "#trans man=trans men",
                "#trans woman=trans women",
                "non-binary",
                "gender dysphoria",
                "#gender euphoria=euphoria",
            ],
        ),
        (
            "a {neutral}/{non-binary}, {abinary} or unaligned {gender identity}",
            ["neutral", "non-binary", "abinary", "gender identity"],
        ),
        ("{transgender} person.", ["transgender"]),
    ],
)
def test_extract_reference(cog: Dictionary, content: str, expected: list[str]):
    assert cog.extract_reference(content) == expected


@pytest.mark.parametrize(
    "content,entities,expected",
    [
        (
            "a {neutral}/{non-binary}, {abinary} or unaligned {gender identity}",
            ["neutral", "non-binary", "abinary", "gender identity"],
            "a [neutral](https://en.pronouns.page/terminology?filter=neutral)/[non-binary](https://en.pronouns.page/terminology?filter=non-binary), [abinary](https://en.pronouns.page/terminology?filter=abinary) or unaligned [gender identity](https://en.pronouns.page/terminology?filter=gender+identity)",
        ),
        (
            "a term referring to people whose {#AGAB=gender assigned at birth} is different than their {gender identity}. It includes {#trans man=trans men} and {#trans woman=trans women} as well as {non-binary} people.",
            [
                "#AGAB=gender assigned at birth",
                "gender identity",
                "#trans man=trans men",
                "#trans woman=trans women",
                "non-binary",
            ],
            "a term referring to people whose [gender assigned at birth](https://en.pronouns.page/terminology?filter=AGAB) is different than their [gender identity](https://en.pronouns.page/terminology?filter=gender+identity). It includes [trans men](https://en.pronouns.page/terminology?filter=trans+man) and [trans women](https://en.pronouns.page/terminology?filter=trans+woman) as well as [non-binary](https://en.pronouns.page/terminology?filter=non-binary) people.",
        ),
        (
            "a person who uses {/he=he/him} pronouns and identifies as a {lesbian}",
            ["/he=he/him", "lesbian"],
            "a person who uses [he/him](https://en.pronouns.page/he) pronouns and identifies as a [lesbian](https://en.pronouns.page/terminology?filter=lesbian)",
        ),
        (
            "from Ancient Greek {http://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.04.0057:entry=a(bro/s=ἁβρός} [habros] - “delicate”",
            [
                "http://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.04.0057:entry=a(bro/s=ἁβρός"
            ],
            "from Ancient Greek [ἁβρός](http://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.04.0057:entry%3Da%2528bro/s) [habros] - “delicate”",
        ),
        (
            "{http://eprints.hud.ac.uk/id/eprint/33535/=Monro i in. z 2017}",
            ["http://eprints.hud.ac.uk/id/eprint/33535/=Monro i in. z 2017"],
            "[Monro i in. z 2017](http://eprints.hud.ac.uk/id/eprint/33535/)",
        ),
    ],
)
def test_format_inline_term_reference(
    cog: Dictionary, content: str, entities: list[str], expected: str
):
    assert cog.format_inline_term_reference(content, entities) == expected


@pytest.mark.parametrize(
    "content,expected",
    [
        (
            "a {neutral}/{non-binary}, {abinary} or unaligned {gender identity}",
            "a [neutral](https://en.pronouns.page/terminology?filter=neutral)/[non-binary](https://en.pronouns.page/terminology?filter=non-binary), [abinary](https://en.pronouns.page/terminology?filter=abinary) or unaligned [gender identity](https://en.pronouns.page/terminology?filter=gender+identity)",
        ),
        (
            "a {man} whose {#AGAB=gender assigned at birth} is or was different than that of their gender (usually, they were {#AFAB=assigned female at birth}).",
            "a [man](https://en.pronouns.page/terminology?filter=man) whose [gender assigned at birth](https://en.pronouns.page/terminology?filter=AGAB) is or was different than that of their gender (usually, they were [assigned female at birth](https://en.pronouns.page/terminology?filter=AFAB)).",
        ),
        (
            "a term referring to people whose {#AGAB=gender assigned at birth} is different than their {gender identity}. It includes {#trans man=trans men} and {#trans woman=trans women} as well as {non-binary} people. Many, but not all, transgender people experience {gender dysphoria} or {#gender euphoria=euphoria}. Some opt for medical {transition} (e.g. {#HRT=hormone replacement therapy} or {#SRS=surgeries}), but not all (they may be unable due to medical, financial or political reasons, or simply may not want to). Some opt for changing their {legal gender} marker, but not all. It should be noted that procedures of changing one's legal gender marker may be difficult or simply non-existent in certain countries; moreover, in many countries there is no option available for {non-binary} people. Whether (and how) a person transitions has no bearing on the validity of their identity.",
            "a term referring to people whose [gender assigned at birth](https://en.pronouns.page/terminology?filter=AGAB) is different than their [gender identity](https://en.pronouns.page/terminology?filter=gender+identity). It includes [trans men](https://en.pronouns.page/terminology?filter=trans+man) and [trans women](https://en.pronouns.page/terminology?filter=trans+woman) as well as [non-binary](https://en.pronouns.page/terminology?filter=non-binary) people. Many, but not all, transgender people experience [gender dysphoria](https://en.pronouns.page/terminology?filter=gender+dysphoria) or [euphoria](https://en.pronouns.page/terminology?filter=gender+euphoria). Some opt for medical [transition](https://en.pronouns.page/terminology?filter=transition) (e.g. [hormone replacement therapy](https://en.pronouns.page/terminology?filter=HRT) or [surgeries](https://en.pronouns.page/terminology?filter=SRS)), but not all (they may be unable due to medical, financial or political reasons, or simply may not want to). Some opt for changing their [legal gender](https://en.pronouns.page/terminology?filter=legal+gender) marker, but not all. It should be noted that procedures of changing one's [legal gender](https://en.pronouns.page/terminology?filter=legal+gender) marker may be difficult or simply non-existent in certain countries; moreover, in many countries there is no option available for [non-binary](https://en.pronouns.page/terminology?filter=non-binary) people. Whether (and how) a person [transition](https://en.pronouns.page/terminology?filter=transition)s has no bearing on the validity of their identity.",
        ),
        # Technically the links are invalid but if locale is to be assumed to be russian, then they actually do work entirely
        (
            "збірний термін, що позначає явища, де призначений при народженні ґендер ({agab}) відрізняється від фактичної ґендерної ідентичності людини. Це включає в себе {#трансфемінність=транс жінок}, {#трансмаскулінність=транс чоловіків} і {#небінарність=небінарних людей}. Деякі, але не всі, трансґендерні люди відчувають ґендерну дісфорію та/або ейфорію. Деякі, але не всі, хочуть пройти через медичний перехід (наприклад, пройти замісну гормональну терапію та/або хірургічні операції). Ті, хто не хоче проходити медичний перехід, можуть мати будь-які причини на це: від політичних до фінансових, або навіть просто цього не хотіти. Деякі хочуть змінити свою стать у паспорті, але не обов'язково всі. Важливо пам'ятати, що в багатьох країнах цей процес є дуже довгим та енерго і фінансово затратним; в деяких він неможливий; а також, що в багатьох країнах не існує варіанту ґендерного маркеру для небінарних людей.",
            "збірний термін, що позначає явища, де призначений при народженні ґендер ([agab](https://en.pronouns.page/terminology?filter=agab)) відрізняється від фактичної ґендерної ідентичності людини. Це включає в себе [транс жінок](https://en.pronouns.page/terminology?filter=%D1%82%D1%80%D0%B0%D0%BD%D1%81%D1%84%D0%B5%D0%BC%D1%96%D0%BD%D0%BD%D1%96%D1%81%D1%82%D1%8C), [транс чоловіків](https://en.pronouns.page/terminology?filter=%D1%82%D1%80%D0%B0%D0%BD%D1%81%D0%BC%D0%B0%D1%81%D0%BA%D1%83%D0%BB%D1%96%D0%BD%D0%BD%D1%96%D1%81%D1%82%D1%8C) і [небінарних людей](https://en.pronouns.page/terminology?filter=%D0%BD%D0%B5%D0%B1%D1%96%D0%BD%D0%B0%D1%80%D0%BD%D1%96%D1%81%D1%82%D1%8C). Деякі, але не всі, трансґендерні люди відчувають ґендерну дісфорію та/або ейфорію. Деякі, але не всі, хочуть пройти через медичний перехід (наприклад, пройти замісну гормональну терапію та/або хірургічні операції). Ті, хто не хоче проходити медичний перехід, можуть мати будь-які причини на це: від політичних до фінансових, або навіть просто цього не хотіти. Деякі хочуть змінити свою стать у паспорті, але не обов'язково всі. Важливо пам'ятати, що в багатьох країнах цей процес є дуже довгим та енерго і фінансово затратним; в деяких він неможливий; а також, що в багатьох країнах не існує варіанту ґендерного маркеру для небінарних людей.",
        ),
    ],
)
def test_format_references(cog: Dictionary, content: str, expected: str):
    assert cog.format_references(content) == expected


@pytest.mark.parametrize(
    "author,expected",
    [
        (None, "Unknown"),
        ("No767", "[No767](https://pronouns.page/@No767)"),
        ("ausir", "[ausir](https://pronouns.page/@ausir)"),
    ],
)
def test_determine_author(cog: Dictionary, author: Optional[str], expected: str):
    assert cog.determine_author(author) == expected
