#include <iostream>

class Me {
    //dynamic cast must have virtual func
    public: virtual ~Me() { }
    public: void print() {
        std::cout << "Hello" << std::endl;
    }
};

class A : public Me {
};

class B {
};

int main() {
    Me me;
    A* a1 = (A*)(&me);
    B* b1 = (B*)(&me);
    std::cout << "a1:" << a1 << ",b1:" << b1 << std::endl;


    A* a2 = static_cast<A*>(&me);
    //B* b2 = static_cast<B*>(&me);
    //std::cout << "a2:" << a2 << ",b2:" << b2 << std::endl;
    std::cout << "a2:" << a2 << std::endl;


    A* a3 = dynamic_cast<A*>(&me);
    B* b3 = dynamic_cast<B*>(&me);
    std::cout << "a3:" << a3 << ",b3:" << b3 << std::endl;
    return 0;
}
