import math
import tileEngine

TILESIZE = tileEngine.TILESIZE

# The Vector class
class Vector:

    # Initialiser
    def __init__(self, p=(0, 0)):
        self.x = p[0]
        self.y = p[1]

    # Returns a string representation of the vector
    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    # Tests the equality of this vector and another
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # Tests the inequality of this vector and another
    def __ne__(self, other):
        return not self.__eq__(other)

        # Returns a tuple with the point corresponding to the vector

    def getP(self):
        return (self.x, self.y)

    # Returns a copy of the vector
    def copy(self):
        v = Vector()
        v.x = self.x
        v.y = self.y
        return v

    # Adds another vector to this vector
    def add(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __add__(self, param):
        return Vector((self.x + param.x, self.y + param.y))

    # Negates the vector (makes it point in the opposite direction)
    def negate(self):
        return self.multiply(-1)

        # Magic method for - (one operand)

    def __neg__(self):
        return self.copy().negate()

    # Subtracts another vector from this vector
    def subtract(self, other):
        return self.add(-other)

    # Magic method for - (two operands)
    def __sub__(self, param):
        return Vector((self.x - param.x, self.y - param.y))

    # Returns the dot product of this vector with another one
    def dot(self, other):
        return self.x * other.x + self.y * other.y

    # Multiplies the vector by a scalar
    def multiply(self, k):
        self.x *= k
        self.y *= k
        return self

    # Magic method for *
    # If the arguments are two vectors, it returns the dot product
    # Otherwise, returns the product by a scalar
    def __mul__(self, param):
        try:
            return self.dot(param)
        except:
            return Vector((self.x * param, self.y * param))

    # Magic method for * when the lefthand side is not a vector
    def __rmul__(self, param):
        return Vector((self.x * param, self.y * param))

    # Divides the vector by a scalar
    def divide(self, k):
        return self.multiply(1 / k)

    # Magic method for /
    def __truediv__(self, param):
        return Vector((self.x / param, self.y / param))

    # Normalizes the vector
    def normalize(self):
        return self.divide(self.length())

    # Returns a normalized version of the vector
    def getNormalized(self):
        return self.copy().normalize()

    # Returns the length of the vector
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    # Returns the squared length of the vector
    def lengthSquared(self):
        return self.x ** 2 + self.y ** 2

    # Reflect this vector on a normal
    def reflect(self, normal):
        n = normal.copy()
        n.multiply(2 * self.dot(normal))
        self.subtract(n)
        return self

    def angle(self):
        return math.atan2(self.y, self.x)

    # convert vector components to integers
    def to_int(self):
        self.x = int(self.x)
        self.y = int(self.y)

    # convert to tilegrid location
    def to_grid(self):
        return Vector((int(self.x // TILESIZE), int(self.y // TILESIZE)))
