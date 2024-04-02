class Characters:
    ListenMan=[
        """            ________""",
        """       r､//   ⌒  ⌒ \\\\""",
        """       |. |1  (● )    (● ) ヽ    %text%""",
        """      .| ^ )      (__人__)     |""",
        """    ._/  ｿ、__  ヽ_/  __//￣｀!""",
        """   /   ｲ                  ｲ7 _/""",
        """   {___//\\               ヽ {"""
    ]
    ThinkMan=[
    """　 　　　＿＿＿_""",
    """　　　／　　 　 　＼ （ ;;;;(""",
    """　 ／　　＿ノ　 ヽ__＼) ;;;;)""",
    """／ 　　 （─） 　（─ /;;／""",
    """|　 　　 　 （__人__） l;;,´　%text%""",
    """/　　　 　 ∩ ノ)━・'／""",
    """(　 ＼　／ ＿ノ´.|　 |""",
    """.＼　 " 　／＿＿|　 |""",
    """"　　＼ ／＿＿＿ ／""",
    ]

def get_character(character:list[str],text:str)->str:
    return "\n".join([line.replace('%text%',text) for line in character])