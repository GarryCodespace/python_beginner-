#include <cmath>
#include <iomanip>
#include <iostream>
#include <memory>
#include <vector>

using namespace std;

const double PI = 3.1415926;

class Shape {
public:
    virtual void show() const = 0;
    virtual double area() const {
        return 0;
    }
    virtual double length() const {
        return 0;
    }
    virtual ~Shape() = default;
};

class Line : public Shape {
private:
    double x1, y1, x2, y2;

public:
    Line(double a, double b, double c, double d)
        : x1(a), y1(b), x2(c), y2(d) {}

    void show() const override {
        cout << "直线: 起点(" << x1 << ", " << y1 << "), 终点("
             << x2 << ", " << y2 << ")";
    }

    double length() const override {
        return sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
    }
};

class Rectangle : public Shape {
private:
    double x, y, width, height;

public:
    Rectangle(double px, double py, double w, double h)
        : x(px), y(py), width(w), height(h) {}

    void show() const override {
        cout << "矩形: 左上角(" << x << ", " << y << "), 宽 "
             << width << ", 高 " << height;
    }

    double area() const override {
        return width * height;
    }
};

class Circle : public Shape {
private:
    double x, y, radius;

public:
    Circle(double px, double py, double r)
        : x(px), y(py), radius(r) {}

    void show() const override {
        cout << "圆形: 圆心(" << x << ", " << y << "), 半径 " << radius;
    }

    double area() const override {
        return PI * radius * radius;
    }

    double length() const override {
        return 2 * PI * radius;
    }
};

vector<unique_ptr<Shape>> shapes;

void addLine() {
    double x1, y1, x2, y2;
    cout << "请输入直线起点 x1 y1: ";
    cin >> x1 >> y1;
    cout << "请输入直线终点 x2 y2: ";
    cin >> x2 >> y2;

    shapes.push_back(make_unique<Line>(x1, y1, x2, y2));
    cout << "直线添加成功。\n";
}

void addRectangle() {
    double x, y, w, h;
    cout << "请输入矩形左上角 x y: ";
    cin >> x >> y;
    cout << "请输入矩形宽和高: ";
    cin >> w >> h;

    shapes.push_back(make_unique<Rectangle>(x, y, w, h));
    cout << "矩形添加成功。\n";
}

void addCircle() {
    double x, y, r;
    cout << "请输入圆心 x y: ";
    cin >> x >> y;
    cout << "请输入半径: ";
    cin >> r;

    shapes.push_back(make_unique<Circle>(x, y, r));
    cout << "圆形添加成功。\n";
}

void showShapes() {
    if (shapes.empty()) {
        cout << "当前没有图形。\n";
        return;
    }

    cout << "\n====== 当前图形列表 ======\n";

    for (size_t i = 0; i < shapes.size(); i++) {
        cout << i + 1 << ". ";
        shapes[i]->show();

        double a = shapes[i]->area();
        double l = shapes[i]->length();

        if (a > 0) {
            cout << "，面积: " << fixed << setprecision(2) << a;
        }

        if (l > 0) {
            cout << "，长度/周长: " << fixed << setprecision(2) << l;
        }

        cout << endl;
    }
}

void deleteShape() {
    if (shapes.empty()) {
        cout << "当前没有图形可删除。\n";
        return;
    }

    showShapes();

    int index;
    cout << "请输入要删除的图形编号: ";
    cin >> index;

    if (index < 1 || index > static_cast<int>(shapes.size())) {
        cout << "编号无效。\n";
        return;
    }

    shapes.erase(shapes.begin() + index - 1);
    cout << "删除成功。\n";
}

void showMenu() {
    cout << "\n====== 小型 CAD 系统 ======\n";
    cout << "1. 添加直线\n";
    cout << "2. 添加矩形\n";
    cout << "3. 添加圆形\n";
    cout << "4. 显示所有图形\n";
    cout << "5. 删除图形\n";
    cout << "0. 退出系统\n";
    cout << "请选择: ";
}

int main() {
    int choice;

    while (true) {
        showMenu();
        cin >> choice;

        switch (choice) {
            case 1:
                addLine();
                break;
            case 2:
                addRectangle();
                break;
            case 3:
                addCircle();
                break;
            case 4:
                showShapes();
                break;
            case 5:
                deleteShape();
                break;
            case 0:
                cout << "CAD 系统已退出。\n";
                return 0;
            default:
                cout << "输入无效，请重新选择。\n";
        }
    }
}
