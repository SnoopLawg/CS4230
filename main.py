class Phone:
    def __init__(self, number, name):
        self.number = number  # Phone number (string)
        self.name = name      # Phone owner's name (string)
        self.state = 'onhook'  # Phone state: 'onhook', 'offhook', 'ringing', 'dialing', 'calling', 'connected'
        self.current_call = None  # Holds the current call participants
        self.ringing_from = None  # Who is calling this phone

    def __str__(self):
        # Return a string representation of the phone's status
        status = f"{self.name} ({self.number}): {self.state}"
        if self.current_call:
            if isinstance(self.current_call, list):
                # In a conference call
                others = ', '.join(p.name for p in self.current_call if p != self)
                status += f" (talking to {others})"
            else:
                # Talking to one other phone
                status += f" (talking to {self.current_call.name})"
        return status

class TelephoneSystem:
    def __init__(self):
        self.phones = {}  # Dictionary to store phones by their number

    def load_phones(self, filename):
        # Load phone numbers and names from a specified file
        with open(filename, 'r') as file:
            for line in file:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        number, name = parts[0], ' '.join(parts[1:])
                        # Validate phone number and name
                        if len(number) == 5 and number.isdigit() and len(name) <= 12 and name.isalpha():
                            self.phones[number] = Phone(number, name)
                        else:
                            print(f"Ignored invalid entry: {line.strip()}")

    def find_phone(self, identifier):
        # Find a phone by number or name
        phone = self.phones.get(identifier)
        if phone:
            return phone
        for p in self.phones.values():
            if p.name == identifier:
                return p
        return None

    def status(self):
        # Display the status of each phone in the system
        for phone in self.phones.values():
            print(phone)

    def offhook(self, identifier):
        # Put a phone offhook
        phone = self.find_phone(identifier)
        if phone:
            if phone.state in ['offhook', 'dialing', 'calling', 'connected']:
                # Already offhook or in a call
                print(f"{phone.name} is already offhook.")
            else:
                phone.state = 'offhook'
                print(f"{phone.name} hears dialtone.")
        else:
            print(f"Phone {identifier} not found.")

    def onhook(self, identifier):
        # Put a phone onhook
        phone = self.find_phone(identifier)
        if phone:
            if phone.state == 'onhook':
                print(f"{phone.name} is already onhook.")
            else:
                # Disconnect from any calls
                if phone.current_call:
                    if isinstance(phone.current_call, list):
                        # Remove this phone from the conference
                        for other in phone.current_call:
                            if other != phone:
                                other.current_call.remove(phone)
                                if len(other.current_call) == 1:
                                    # Only one other phone left, change to normal call
                                    other.current_call = other.current_call[0]
                                    other.state = 'connected'
                        phone.current_call = None
                    else:
                        # Disconnect from the other phone
                        other = phone.current_call
                        other.current_call = None
                        if other.state != 'onhook':
                            other.state = 'offhook'
                            print(f"{other.name} hears silence.")
                        phone.current_call = None
                    phone.state = 'onhook'
                elif phone.state == 'ringing':
                    # Missed call
                    phone.state = 'onhook'
                    caller = phone.ringing_from
                    if caller and caller.state == 'calling':
                        print(f"{caller.name} hears silence.")
                        caller.state = 'offhook'
                        caller.current_call = None
                        caller.ringing_to = None
                    phone.ringing_from = None
                else:
                    phone.state = 'onhook'
                print(f"{phone.name} is now onhook.")
        else:
            print(f"Phone {identifier} not found.")

    def call(self, caller_id, receiver_id):
        # Initiate a call from one phone to another
        caller = self.find_phone(caller_id)
        receiver = self.find_phone(receiver_id)

        if not caller:
            print(f"Caller {caller_id} not found.")
            return
        if not receiver:
            print(f"{caller.name} hears denial.")
            return

        if caller.state != 'offhook':
            print(f"{caller.name} hears silence.")
            return

        if receiver.state == 'onhook':
            # Set up the call
            caller.state = 'calling'
            caller.current_call = receiver
            receiver.state = 'ringing'
            receiver.ringing_from = caller
            print(f"{caller.name} hears ringback.")
            print(f"{receiver.name} hears ringing.")
        elif receiver.state in ['offhook', 'dialing', 'calling', 'connected', 'ringing']:
            print(f"{caller.name} hears busy.")
        else:
            print(f"{caller.name} hears denial.")

    def answer_call(self, identifier):
        # Answer a ringing phone
        phone = self.find_phone(identifier)
        if phone:
            if phone.state == 'ringing':
                caller = phone.ringing_from
                phone.state = 'connected'
                phone.current_call = caller
                caller.state = 'connected'
                print(f"{caller.name} and {phone.name} are talking.")
            else:
                print(f"{phone.name} is not ringing.")
        else:
            print(f"Phone {identifier} not found.")

    def transfer(self, identifier, new_receiver_id):
        # Transfer an ongoing call to a new phone
        caller = self.find_phone(identifier)
        new_receiver = self.find_phone(new_receiver_id)

        if not caller or not new_receiver:
            print(f"{identifier} hears denial.")
            return

        if caller.state != 'connected' or not caller.current_call:
            print(f"{caller.name} hears denial.")
            return

        other_party = caller.current_call
        if isinstance(other_party, list):
            # Cannot transfer a conference call
            print(f"{caller.name} hears denial.")
            return

        if new_receiver.state == 'onhook':
            # Begin transfer process
            caller.state = 'calling'
            caller.current_call = new_receiver
            new_receiver.state = 'ringing'
            new_receiver.ringing_from = caller
            print(f"{caller.name} hears ringback.")
            print(f"{new_receiver.name} hears ringing.")
            # When new_receiver answers, connect new_receiver and other_party
            # For simplicity, we'll assume the transfer is completed when new_receiver goes offhook
        else:
            print(f"{caller.name} hears denial.")

    def conference(self, identifier, third_party_id):
        # Add a third party to an ongoing call
        caller = self.find_phone(identifier)
        third_party = self.find_phone(third_party_id)

        if not caller or not third_party:
            print(f"{identifier} hears denial.")
            return

        if caller.state != 'connected' or not caller.current_call:
            print(f"{caller.name} hears denial.")
            return

        if third_party.state == 'onhook':
            other_party = caller.current_call
            if isinstance(other_party, list):
                if len(other_party) >= 3:
                    print(f"{caller.name} hears denial.")
                    return
                participants = other_party + [third_party]
            else:
                participants = [caller, other_party, third_party]
            # Begin conference process
            caller.state = 'calling'
            caller.current_call = participants
            third_party.state = 'ringing'
            third_party.ringing_from = caller
            print(f"{caller.name} hears ringback.")
            print(f"{third_party.name} hears ringing.")
            # When third_party answers, all are connected
        else:
            print(f"{caller.name} hears denial.")

    def pickup(self, identifier):
        # Handle a phone going offhook
        phone = self.find_phone(identifier)
        if not phone:
            print(f"Phone {identifier} not found.")
            return

        if phone.state == 'onhook':
            self.offhook(identifier)
        elif phone.state == 'ringing':
            self.answer_call(identifier)
        else:
            print(f"{phone.name} hears silence.")

def main():
    system = TelephoneSystem()
    system.load_phones('phones.txt')

    while True:
        command = input("Enter command: ").strip()
        if not command:
            continue
        command_parts = command.split()
        if command.lower() == "status":
            system.status()
        elif len(command_parts) == 2:
            phone_id, action = command_parts
            action = action.lower()
            if action == "offhook":
                system.pickup(phone_id)
            elif action == "onhook":
                system.onhook(phone_id)
            else:
                print("Invalid command.")
        elif len(command_parts) == 3:
            phone_id, action, target_id = command_parts
            action = action.lower()
            if action == "call":
                system.call(phone_id, target_id)
            elif action == "transfer":
                system.transfer(phone_id, target_id)
            elif action == "conference":
                system.conference(phone_id, target_id)
            else:
                print("Invalid command.")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
