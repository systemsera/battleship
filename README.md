# battleship v0.5
a tkinter(-table) based program that lets you play battleship using a distributed ledger (IOTA Tangle) as its data transfer backend

In order to play battleship you and your opponent will each need an IOTA address.

Set up:

1) In the options tab you will be able to save your target address as well as your own (fleet-)address, with the target address being your enemies (fleet-)address. Pass your own address to your enemy and put it into the Address-field. For your enemy this setup is exactly vice-ersa. Your enemy will have to transmit his address to you and paste it into his Address-field. The addresses you transmitted to one another can then be pasted into each others Target Address-field. (You can ignore both seed and node settings for now, the node is a public remote PoW server and currently hardcoded into the source. The seed your transactions are sent from will be generated at random by the IOTA API.)

2) Once you have pasted  your enemies address and your own into the respective fields, click the Save-button.

Game start:

3) Back in the Bridge-tab you may now click into your own fleet table and place a total of 5 ships. These will be depicted as the capital letter 'S'.

4) You can now click a field in the enemy fleet table where you suspect your enemy may have placed one of his ships and click the Fire-button. The program will let you know if the transaction generation was successful. You may try fireing again if it wasn't.

5) Once you and your enemy have both fired a shot, you can check incoming enemy projectiles by clicking the Check-button. An incoming projectile will be market on your fleet table.


A lower-case 'o' signifies a drop into the ocean, while a capital 'X' will be drawn onto the table if it is a direct hit. Since the program cannot yet update your or your enemies' enemy fleet table, you'll have to use other means to communicate whether or not his projectile successfully hit a ship.

This current build (0.9) is a code example of how to transfer data to the IOTA network as well as fetching data from it based on the initial address of the transaction, decoding trytes back into intelligible binary / ASCII and passing it to tkintertable.
