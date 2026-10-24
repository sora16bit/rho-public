from rho.charkind import char_kind, word_goshu

def test_char_kind_basic():
    assert char_kind("漢") == "kanji"
    assert char_kind("あ") == "hiragana"
    assert char_kind("ア") == "katakana"
    assert char_kind("a") == "other"

def test_word_goshu_kango():
    # 漢字主体 → 漢語
    assert word_goshu("国際", "コクサイ") == "kango"

def test_word_goshu_wago():
    # ひらがな/送り仮名を含む活用語・和語
    assert word_goshu("食べる", "タベル") == "wago"
    assert word_goshu("まだ", "マダ") == "wago"

def test_word_goshu_gairaigo():
    # カタカナ主体 → 外来語
    assert word_goshu("コンピューター", "コンピューター") == "gairaigo"

def test_word_goshu_kigou():
    assert word_goshu("。", "。") == "kigou"
