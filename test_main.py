import unittest
from main import TelephoneSystem, Phone

class TestTelephoneSystem(unittest.TestCase):
    def setUp(self):
        # Initialize the TelephoneSystem and add phones for testing
        self.system = TelephoneSystem()
        self.system.phones = {
            "12345": Phone("12345", "Alice"),
            "23456": Phone("23456", "Bob"),
            "34567": Phone("34567", "Charlie"),
        }

    #TEST CASES 1-10 per TestPlan.docx

    # Test Case 1: Normal Call Workflow
    def test_normal_call_workflow(self):
        self.system.offhook("12345") #Alice picks up the phone.
        self.system.call("12345", "23456") #Alice calls Bob, hears dial tone. Bob hearing ringing.
        self.system.offhook("23456") #Bob and Alice are talking.
        self.system.onhook("23456")#Bob ends call, Alice hears silence.
        # Expected Results
        self.assertEqual(self.system.phones["12345"].state, "offhook") #Alice should still be on the phone, hearing silence.
        self.assertEqual(self.system.phones["23456"].state, "onhook") #Bob hung up so he should be onhook.

    # Test Case 2: Conference Call Workflow
    def test_conference_call_workflow(self):
        self.system.offhook("12345") #Alice picks up the phone.
        self.system.call("12345", "23456") #Alice calls Bob and hears dial tone. Bob hears ringing.
        self.system.offhook("23456") #Bob and Alice are talking.
        self.system.conference("12345", "34567") #Alice initiates a conference by adding Charlie to the call. Charlie hears ringing. Alice hears dial tone.
        self.system.offhook("34567") #Charlie, Alice, and Bob are in a conference now.
        self.system.onhook("12345") #Alice hangs up, leaving Charlie and Bob on call.           THERE"S A BUG HERE!!!!! Status will show Alice as part of the call even if she's onhook.
        # Expected Results
        self.assertEqual(self.system.phones["12345"].state, "onhook") #Alice is not on the call
        self.assertEqual(self.system.phones["23456"].state, "connected") #Bob is talking with Charlie still.
        self.assertEqual(self.system.phones["34567"].state, "connected") #Charlie is talking with Bob still.
        #self.assertEqual(self.system.phones["12345"].status, "test if she's no longer part of the conference status") FOR THE BUG when Alice leaves a conference.

    # Test Case 3: Call Transfer Workflow
    def test_call_transfer_workflow(self):
        self.system.offhook("12345") #Alice picks up the phone.
        self.system.call("12345", "23456") #Alice calls Bob and hears dial tone. Bob hears ringing.
        self.system.offhook("23456") #Bob and Alice are talking.
        self.system.transfer("12345", "34567") #Alice transfers Bob to Charlie. Charlie hears ringing. Bob hears dial tone.
        self.system.offhook("34567") #Charlie and Bob are speaking.
        # Expected Results
        self.assertEqual(self.system.phones["23456"].current_call.name, "Charlie") #Shows the call was transferred to Charlie with Bob on.
        self.assertEqual(self.system.phones["12345"].state, "offhook") #Alice should be offhooked automatically after transferring Bob to Charlie.

    # Test Case 4: Busy Signal Test
    def test_busy_signal(self):
        self.system.offhook("12345") #Alice picks up her phone.
        self.system.call("12345", "23456")#Alice calls Bob and hears dial tone. Bob hears ringing.
        self.system.offhook("23456") #Bob and Alice are now talking.
        self.system.offhook("34567") #Charlie picks up his phone.
        self.system.call("34567", "12345") #Charlie calls Alice.
        # Expected Result: Carol hears busy
        # We might want to adjust this assertion based on the output method
        self.assertEqual(self.system.phones["34567"].state, "offhook") #This shows taht Charlie is now offhook. I'm going to come back to this one.

    # Test Case 5: Illegal Phone Number Test
    def test_illegal_phone_number(self):
        self.system.offhook("12345") #Alice picks up her phone.
        result = self.system.call("12345", "00000")  # Alice calls a number that doesn't exist.
        self.assertIn("hears denial", result) #Alice should hear a denaial.

    # Test Case 6: Onhook Command Without Offhook
    def test_onhook_without_offhook(self): #All numbers need to start as offhook for this test too perform correctly.
        result = self.system.call("12345", "23456") #Alice (without going offhook) calls Bob.
        self.assertIn("hears silence", result) #Alice should hear silence.

    # Test Case 7: Offhook While Already Offhook
    def test_offhook_while_already_offhook(self):
        self.system.offhook("12345") #Setting Alice to offhook, she picks up her phone.
        result = self.system.offhook("12345")#Test going offhook when she's already offhook.
        #We've chosen to not perform any actions if she goes offhook while offhook.
        self.assertEqual(self.system.phones["12345"].state, "offhook") #No actions taken.

    # Test Case 8: Maximum Conference Participants
    def test_max_conference_participants(self):
        self.system.offhook("12345") #Alice picks up her phone, hears silence.
        self.system.call("12345", "23456") #Alice calls bob and hears dial tone. Bob hears ringing.
        self.system.offhook("23456")#Bob and Alice are now talking.
        self.system.conference("12345", "34567")#Alice initiates a conference by adding Charlie. Alice hears dial tone. Charlie hears ringing.
        self.system.offhook("34567") #Charlie joins the conference with Bob and Alice.
        result = self.system.conference("12345", "45678") #Have Alice try to conference Sally.
        self.assertIn("hears denial", result) #Alice should hear a denial. Sally should not hear ringing.

    # Test Case 9: Status Command Test
    def test_status_command(self):
        self.system.offhook("12345") #Alice picks up her phone, hears silence.
        self.system.call("12345", "23456") #Alice calls Bob and hears dial tone. Bob hears ringing.
        self.system.offhook("23456")#Bob and Alice are now talking.
        status = self.system.status() #Check the status of the call.
        self.assertIn("talking", status) #Should say talking. This can build out more to test other statuses still. Only testing talking so far.

    # Test Case 10: Invalid Command Test
    def test_invalid_command(self):
        result = self.system.call("99999", "00000")  #Entering numbers that don't exist in phones.txt file...
        self.assertIn("Invalid command", result) #Should see "Invalid command."

if __name__ == "__main__":
    unittest.main()
