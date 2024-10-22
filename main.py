class Phone:
    def __init__(self, number, name):
        self.number = number  # Store the phone number
        self.name = name      # Store the phone owner's name
        self.offhook = False  # Indicates whether the phone is offhook (in use)
        self.calling = None   # Holds the currently connected phone(s)

    def __str__(self):
        # Return a string representation of the phone's status
        status = "offhook" if self.offhook else "onhook"
        return f"{self.name} ({self.number}): {status}"

class TelephoneSystem:
    def __init__(self):
        self.phones = {}  # Dictionary to store phones by their number

    def load_phones(self, filename):
        # Load phone numbers and names from a specified file
        with open(filename, 'r') as file:
            for line in file:
                number, name = line.strip().split()  # Split the line into number and name
                self.phones[number] = Phone(number, name)  # Create Phone objects

    def find_phone(self, identifier):
        # Find a phone by number or name
        return self.phones.get(identifier) or next((p for p in self.phones.values() if p.name == identifier), None)

    def status(self):
        # Display the status of each phone in the system
        for phone in self.phones.values():
            print(phone)  # Print phone information
            if phone.calling:
                # If the phone is currently in a call
                if isinstance(phone.calling, list):
                    # If it's a conference call with multiple participants
                    talkers = ', '.join(p.name for p in phone.calling)
                    print(f"  Talking to: {talkers}")  # List all participants
                else:
                    print(f"  Talking to: {phone.calling.name}")  # Print single participant's name

    def offhook(self, identifier):
        # Put a phone offhook (in use)
        phone = self.find_phone(identifier)
        if phone:
            if phone.offhook:
                print(f"{phone.name} hears silence.")  # Already offhook
            else:
                phone.offhook = True  # Change status to offhook
                print(f"{phone.name} hears dialtone.")  # Notify user

    def onhook(self, identifier):
        # Put a phone onhook (not in use)
        phone = self.find_phone(identifier)
        if phone:
            if phone.offhook:
                phone.offhook = False  # Change status to onhook
                phone.calling = None    # Clear the current call
                print(f"{phone.name} is now onhook.")

    def call(self, caller_id, receiver_id):
        # Initiate a call from one phone to another
        caller = self.find_phone(caller_id)
        receiver = self.find_phone(receiver_id)

        if caller and receiver:
            if not caller.offhook:
                print(f"{caller.name} hears silence.")  # Caller is onhook
                return
            if receiver.offhook:
                print(f"{caller.name} hears busy.")  # Receiver is already on a call
                return
            caller.calling = receiver  # Connect the two phones
            receiver.calling = caller
            print(f"{caller.name} hears ringback.")
            print(f"{receiver.name} hears ringing.")
            print(f"{caller.name} and {receiver.name} are talking.")  # Notify both users
        else:
            print(f"{caller.name} hears denial.")  # One of the phones is invalid

    def transfer(self, caller_id, new_receiver_id):
        # Transfer an ongoing call to a new phone
        caller = self.find_phone(caller_id)
        new_receiver = self.find_phone(new_receiver_id)

        if caller and new_receiver:
            if caller.calling:
                caller.calling = new_receiver  # Transfer the call
                print(f"{caller.name} hears ringback.")
                print(f"{new_receiver.name} hears ringing.")
                print(f"{new_receiver.name} hears silence.")  # New receiver is now connected
                print(f"{caller.name} has transferred the call to {new_receiver.name}.")
            else:
                print(f"{caller.name} hears denial.")  # No active call to transfer
        else:
            print(f"{caller.name} hears denial.")  # One of the phones is invalid

    def conference(self, caller_id, third_party_id):
        # Start a conference call with a third party
        caller = self.find_phone(caller_id)
        third_party = self.find_phone(third_party_id)

        if caller and caller.calling and third_party:
            # If the caller is already on a call and the third party is valid
            caller.calling = [caller.calling, third_party]  # Add the third party to the call
            print(f"{caller.name} hears ringback.")
            print(f"{third_party.name} hears ringing.")
            print(f"{third_party.name} hears silence.")
            print(f"{caller.name}, {caller.calling[0].name}, and {third_party.name} are talking.")
        else:
            print(f"{caller.name} hears denial.")  # Invalid call setup

def main():
    system = TelephoneSystem()  # Create a new telephone system
    system.load_phones('phones.txt')  # Load phones from a file

    while True:
        command = input("Enter command: ").strip().split()  # Read user input
        if not command:
            continue

        cmd = command[0].lower()  # Get the command type
        if cmd == "status":
            system.status()  # Show system status
        elif cmd == "phone" and command[1] == "offhook":
            system.offhook(command[2])  # Put phone offhook
        elif cmd == "phone" and command[1] == "onhook":
            system.onhook(command[2])  # Put phone onhook
        elif cmd == "phone" and command[1] == "call":
            system.call(command[2], command[3])  # Make a call
        elif cmd == "phone" and command[1] == "transfer":
            system.transfer(command[2], command[3])  # Transfer a call
        elif cmd == "phone" and command[1] == "conference":
            system.conference(command[2], command[3])  # Start a conference call
        else:
            print("Invalid command.")  # Handle invalid commands

if __name__ == "__main__":
    main()