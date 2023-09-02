import discord
from libs.cog_utils.pronouns import convert_to_proper_sentence, parse_pronouns_sentence


class PronounsTesterModal(discord.ui.Modal, title="Input the fields"):
    def __init__(self, sentence: str, name: str):
        super().__init__()
        self.sentence = sentence
        self.name = name
        self.sp = discord.ui.TextInput(
            label="Subjective Pronoun", placeholder="Example: They | He | She"
        )
        self.op = discord.ui.TextInput(
            label="Objective Pronoun", placeholder="Example: Them | Him | Her "
        )
        self.pd = discord.ui.TextInput(
            label="Possessive Determiner", placeholder="Example: Their | His | Her"
        )
        self.pp = discord.ui.TextInput(
            label="Possessive Pronoun", placeholder="Example: Theirs | His | Hers"
        )
        self.rp = discord.ui.TextInput(
            label="Reflective Pronoun",
            placeholder="Example: Themselves | Himself | Herself",
        )

        self.add_item(self.sp)
        self.add_item(self.op)
        self.add_item(self.pd)
        self.add_item(self.pp)
        self.add_item(self.rp)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        # The new Regex-based solution to the pronouns tester command
        # Original: https://github.com/LilbabxJJ-1/PrideBot/blob/master/commands/pronouns.py#L15
        replacements = {
            "$subjective_pronoun": self.sp.value.lower(),
            "$objective_pronoun": self.op.value.lower(),
            "$possessive_pronoun": self.pp.value.lower(),
            "$possessive_determiner": self.pd.value.lower(),
            "$reflective_pronoun": self.rp.value.lower(),
            "$name": self.name.lower(),
        }
        parsed_sentence = parse_pronouns_sentence(replacements, self.sentence)
        complete_sentence = convert_to_proper_sentence(parsed_sentence)
        await interaction.response.send_message(complete_sentence)
