import discord


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
        # TODO - Regex based solution
        complete_sentence = (
            self.sentence.replace("$subjective_pronoun", self.sp.value.lower())
            .replace("$objective_pronoun", self.op.value.lower())
            .replace("$possessive_pronoun", self.pp.value.lower())
            .replace("$reflective_pronoun", self.rp.value.lower())
            .replace("$name", self.name)
        )
        await interaction.response.send_message(complete_sentence)
