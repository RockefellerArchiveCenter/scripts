from ford_grants_notes import add_semicolon_spaces, handle_fap_title, to_sentence_case

def test_add_semicolon_spaces():
    for input, expected in [
            ("foo;bar;baz", "foo; bar; baz"),
            ("123;456;789;", "123; 456; 789;"),
            ("foo; bar;baz", "foo; bar; baz"),
            ("foo1;bar2;3baz", "foo1; bar2; 3baz")]:
        assert add_semicolon_spaces(input) == expected

def test_to_sentence_case():
    for input, expected in [
            ("THIS IS A STRING.", "This is a string."),
            ("TRY THIS. AND THIS.", "Try this. And this."),
            ("I DID NOT KNOW THE ANSWER; IT WAS ALL TOO CLEAR.", "I did not know the answer; it was all too clear."),
            ("IT WAS DARK. And stormy.", "It was dark. And stormy.")]:
        assert to_sentence_case(input) == expected


def test_handle_fap_title():
    for input, expected in [
            ("Foundation-Administered Project (FAP) (06390191): TRAINING PROGRAM FOR ASSOCIATES IN OVERSEAS DEVELOPMENT IN LATIN AMERICA AND THE CARIBBEAN",
             "Foundation-Administered Project (FAP) (06390191): Training Program For Associates In Overseas Development In Latin America And The Caribbean"),
             ("Foundation-Administered Project (FAP) (06390191): TRAINING PROGRAM FOR ASSOCIATES: IN OVERSEAS DEVELOPMENT IN LATIN AMERICA AND THE CARIBBEAN",
              "Foundation-Administered Project (FAP) (06390191): Training Program For Associates: In Overseas Development In Latin America And The Caribbean")
             ]:
        assert handle_fap_title(input) == expected

if __name__ == "__main__":
    test_add_semicolon_spaces()
    test_to_sentence_case()
