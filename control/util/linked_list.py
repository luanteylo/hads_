from typing import List, Any, Dict


class Node:

    def __init__(self, data=None):
        self.data = data
        self.next = None


class LinkedList:
    head: Node

    def __init__(self):
        self.head = None
        self.tail = None

        self.size = 0

    def add_at_end(self, new_data):
        """
        add node at end of the linked list
        :param new_data:
        """

        self.size += 1

        new_node = Node(new_data)

        if self.head is None:
            self.head = new_node
            self.tail = new_node
            return

        self.tail.next = new_node
        self.tail = self.tail.next

    def add_ordered(self, new_data):
        """
        add node ordered at the linked list
        :param new_data:
        """

        if not hasattr(new_data, '__lt__'):
            raise Exception("LinkedList Error: Obj '{}' don't have attribute '__eq__'".format(new_data))

        self.size += 1

        new_node = Node(new_data)

        if self.head is None:
            self.head = new_node
            self.tail = new_node
            return

        ant = None
        aux = self.head

        while aux is not None and aux.data < new_data:
            ant = aux
            aux = aux.next

        if aux is None:
            ant.next = new_node
            self.tail = new_node
        else:
            new_node.next = aux

            if ant is not None:
                ant.next = new_node
            else:
                self.head = new_node

    def pop(self):

        data = None
        if self.head is not None:
            data = self.head.data
            self.head = self.head.next

            # UPDATE SIZE
            self.size = self.size - 1

        return data

    def clear(self):
        self.tail = self.head = None
        self.size = 0

    def print_list(self):
        print_node = self.head

        while print_node is not None:
            print(print_node.data)
            print_node = print_node.next

    def __remove(self, element):
        aux = self.head
        ant = None

        while aux is not None:

            if aux.data == element:

                if self.size == 1:
                    self.head = None
                    self.tail = None
                else:
                    if ant is None:
                        self.head = aux.next
                    else:
                        ant.next = aux.next
                        aux.next = None

                self.size -= 1

                return

            ant = aux
            aux = aux.next

    def remove(self, elements: List[Any]):

        for element in elements:
            self.__remove(element)
