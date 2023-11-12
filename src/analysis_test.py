import unittest
import discord
from discord.ext import commands


BLM_LOG_URL = "https://xivanalysis.com/fflogs/tzWm98Pa31khHRNY/1/10"
RDM_LOG_URL = "https://xivanalysis.com/fflogs/nkb6KzwhTV7XJ8dC/123/1559"
SMN_LOG_URL = "https://xivanalysis.com/fflogs/1pW6XKy8CxZQfnb2/1/1"
DNC_LOG_URL = "https://xivanalysis.com/fflogs/k7VvHCP38rqDFfQm/17/201"
BRD_LOG_URL = "https://xivanalysis.com/fflogs/mjcBPQRw3DW2rnzG/8/300"
MCH_LOG_URL = "https://xivanalysis.com/fflogs/1pW6XKy8CxZQfnb2/1/7"
RPR_LOG_URL = "https://xivanalysis.com/fflogs/Rj61r9ChBfpcVvYx/2/7"
DRG_LOG_URL = "https://xivanalysis.com/fflogs/qfRP2HyVw7xN98kC/1/2"
SAM_LOG_URL = "https://xivanalysis.com/fflogs/HJfrvwpP6LcNxFVY/9/1"
NIN_LOG_URL = "https://xivanalysis.com/fflogs/1pW6XKy8CxZQfnb2/1/3"
MNK_LOG_URL = "https://xivanalysis.com/fflogs/79xwHGQNagB1Rzc6/15/335"
WAR_LOG_URL = "https://xivanalysis.com/fflogs/T9KZGQRV2FfAgbYB/5/2"
GNB_LOG_URL = "https://xivanalysis.com/fflogs/aqK1tYgzQZLBn76f/2/46"
PLD_LOG_URL = "https://xivanalysis.com/fflogs/Rj61r9ChBfpcVvYx/2/2"
DRK_LOG_URL = "https://xivanalysis.com/fflogs/2ATn1cQdWF9hvpZz/25/3"
WHM_LOG_URL = "https://xivanalysis.com/fflogs/Rj61r9ChBfpcVvYx/2/3"
AST_LOG_URL = "https://xivanalysis.com/fflogs/79xwHGQNagB1Rzc6/15/390"
SGE_LOG_URL = "https://xivanalysis.com/fflogs/HJfrvwpP6LcNxFVY/9/4"
SCH_LOG_URL = "https://xivanalysis.com/fflogs/nkb6KzwhTV7XJ8dC/123/445"

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        cogs = {"basic_cmds"}
        intents = discord.Intents.default()

    def test_blm(self):
        pass
