#import <Cocoa/Cocoa.h>

#include <algorithm>
#include <cmath>
#include <vector>

enum class Tool {
    Line,
    Circle,
    Rectangle,
    Triangle
};

struct CadPoint {
    double x;
    double y;
};

struct Shape {
    Tool tool;
    CadPoint start;
    CadPoint end;
};

static NSRect RectFromPoints(CadPoint a, CadPoint b) {
    CGFloat x = std::min(a.x, b.x);
    CGFloat y = std::min(a.y, b.y);
    CGFloat width = std::abs(a.x - b.x);
    CGFloat height = std::abs(a.y - b.y);
    return NSMakeRect(x, y, width, height);
}

@interface DrawingView : NSView {
    std::vector<Shape> shapes;
    Shape previewShape;
    Tool currentTool;
    bool isDrawing;
}
- (void)setTool:(Tool)tool;
- (void)clearCanvas;
- (void)saveDrawing;
@end

@implementation DrawingView

- (instancetype)initWithFrame:(NSRect)frame {
    self = [super initWithFrame:frame];
    if (self) {
        currentTool = Tool::Line;
        isDrawing = false;
        self.wantsLayer = YES;
        self.layer.backgroundColor = [[NSColor whiteColor] CGColor];
    }
    return self;
}

- (BOOL)acceptsFirstResponder {
    return YES;
}

- (BOOL)isFlipped {
    return YES;
}

- (void)viewDidMoveToWindow {
    [self.window makeFirstResponder:self];
}

- (void)setTool:(Tool)tool {
    currentTool = tool;
}

- (void)clearCanvas {
    shapes.clear();
    isDrawing = false;
    [self setNeedsDisplay:YES];
}

- (CadPoint)pointFromEvent:(NSEvent *)event {
    NSPoint location = [self convertPoint:event.locationInWindow fromView:nil];
    return CadPoint{location.x, location.y};
}

- (void)drawGrid {
    [[NSColor colorWithCalibratedWhite:0.92 alpha:1.0] setStroke];
    for (int x = 0; x < self.bounds.size.width; x += 25) {
        NSBezierPath *line = [NSBezierPath bezierPath];
        [line moveToPoint:NSMakePoint(x, 0)];
        [line lineToPoint:NSMakePoint(x, self.bounds.size.height)];
        [line stroke];
    }
    for (int y = 0; y < self.bounds.size.height; y += 25) {
        NSBezierPath *line = [NSBezierPath bezierPath];
        [line moveToPoint:NSMakePoint(0, y)];
        [line lineToPoint:NSMakePoint(self.bounds.size.width, y)];
        [line stroke];
    }
}

- (void)drawShape:(const Shape &)shape preview:(BOOL)isPreview {
    NSBezierPath *path = [NSBezierPath bezierPath];
    [path setLineWidth:isPreview ? 2.0 : 3.0];
    [path setLineCapStyle:NSLineCapStyleRound];
    [path setLineJoinStyle:NSLineJoinStyleRound];

    if (shape.tool == Tool::Line) {
        [path moveToPoint:NSMakePoint(shape.start.x, shape.start.y)];
        [path lineToPoint:NSMakePoint(shape.end.x, shape.end.y)];
    } else if (shape.tool == Tool::Circle) {
        NSRect rect = RectFromPoints(shape.start, shape.end);
        CGFloat side = std::min(rect.size.width, rect.size.height);
        rect.size = NSMakeSize(side, side);
        [path appendBezierPathWithOvalInRect:rect];
    } else if (shape.tool == Tool::Rectangle) {
        [path appendBezierPathWithRect:RectFromPoints(shape.start, shape.end)];
    } else if (shape.tool == Tool::Triangle) {
        NSRect rect = RectFromPoints(shape.start, shape.end);
        NSPoint top = NSMakePoint(NSMidX(rect), NSMinY(rect));
        NSPoint left = NSMakePoint(NSMinX(rect), NSMaxY(rect));
        NSPoint right = NSMakePoint(NSMaxX(rect), NSMaxY(rect));
        [path moveToPoint:top];
        [path lineToPoint:left];
        [path lineToPoint:right];
        [path closePath];
    }

    if (isPreview) {
        CGFloat pattern[] = {8.0, 5.0};
        [path setLineDash:pattern count:2 phase:0.0];
        [[NSColor systemBlueColor] setStroke];
    } else {
        [[NSColor blackColor] setStroke];
    }
    [path stroke];
}

- (void)drawRect:(NSRect)dirtyRect {
    [[NSColor whiteColor] setFill];
    NSRectFill(self.bounds);

    [self drawGrid];

    for (const Shape &shape : shapes) {
        [self drawShape:shape preview:NO];
    }

    if (isDrawing) {
        [self drawShape:previewShape preview:YES];
    }
}

- (void)mouseDown:(NSEvent *)event {
    isDrawing = true;
    CadPoint point = [self pointFromEvent:event];
    previewShape = Shape{currentTool, point, point};
    [self setNeedsDisplay:YES];
}

- (void)mouseDragged:(NSEvent *)event {
    if (!isDrawing) {
        return;
    }

    previewShape.end = [self pointFromEvent:event];
    [self setNeedsDisplay:YES];
}

- (void)mouseUp:(NSEvent *)event {
    if (!isDrawing) {
        return;
    }

    previewShape.end = [self pointFromEvent:event];
    shapes.push_back(previewShape);
    isDrawing = false;
    [self setNeedsDisplay:YES];
}

- (void)keyDown:(NSEvent *)event {
    NSString *key = event.charactersIgnoringModifiers.lowercaseString;

    if ([key isEqualToString:@"c"]) {
        [self clearCanvas];
        return;
    }

    if ([key isEqualToString:@"s"]) {
        [self saveDrawing];
        return;
    }

    [super keyDown:event];
}

- (void)saveDrawing {
    NSBitmapImageRep *bitmap = [self bitmapImageRepForCachingDisplayInRect:self.bounds];
    [self cacheDisplayInRect:self.bounds toBitmapImageRep:bitmap];
    NSData *pngData = [bitmap representationUsingType:NSBitmapImageFileTypePNG properties:@{}];

    NSString *path = [NSHomeDirectory() stringByAppendingPathComponent:@"Desktop/cad_drawing.png"];
    [pngData writeToFile:path atomically:YES];

    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"保存成功";
    alert.informativeText = [NSString stringWithFormat:@"图片已保存到 %@", path];
    [alert addButtonWithTitle:@"OK"];
    [alert runModal];
}

@end

@interface AppDelegate : NSObject <NSApplicationDelegate>
@property(strong) NSWindow *window;
@property(strong) DrawingView *drawingView;
@property(strong) NSMutableArray<NSButton *> *toolButtons;
@end

@implementation AppDelegate

- (NSButton *)buttonWithTitle:(NSString *)title action:(SEL)action {
    NSButton *button = [NSButton buttonWithTitle:title target:self action:action];
    button.bezelStyle = NSBezelStyleTexturedRounded;
    button.translatesAutoresizingMaskIntoConstraints = NO;
    return button;
}

- (void)selectButton:(NSButton *)selected {
    for (NSButton *button in self.toolButtons) {
        button.state = button == selected ? NSControlStateValueOn : NSControlStateValueOff;
    }
}

- (void)chooseLine:(NSButton *)sender {
    [self.drawingView setTool:Tool::Line];
    [self selectButton:sender];
}

- (void)chooseCircle:(NSButton *)sender {
    [self.drawingView setTool:Tool::Circle];
    [self selectButton:sender];
}

- (void)chooseRectangle:(NSButton *)sender {
    [self.drawingView setTool:Tool::Rectangle];
    [self selectButton:sender];
}

- (void)chooseTriangle:(NSButton *)sender {
    [self.drawingView setTool:Tool::Triangle];
    [self selectButton:sender];
}

- (void)clearCanvas:(NSButton *)sender {
    [self.drawingView clearCanvas];
}

- (void)saveCanvas:(NSButton *)sender {
    [self.drawingView saveDrawing];
}

- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    NSRect frame = NSMakeRect(100, 100, 980, 720);
    self.window = [[NSWindow alloc] initWithContentRect:frame
                                              styleMask:NSWindowStyleMaskTitled |
                                                        NSWindowStyleMaskClosable |
                                                        NSWindowStyleMaskResizable |
                                                        NSWindowStyleMaskMiniaturizable
                                                backing:NSBackingStoreBuffered
                                                  defer:NO];

    self.window.title = @"小型 CAD 系统 - 点击工具后拖动画图";

    NSView *content = [[NSView alloc] initWithFrame:frame];
    content.translatesAutoresizingMaskIntoConstraints = NO;
    self.window.contentView = content;

    NSStackView *toolbar = [[NSStackView alloc] init];
    toolbar.orientation = NSUserInterfaceLayoutOrientationHorizontal;
    toolbar.alignment = NSLayoutAttributeCenterY;
    toolbar.spacing = 10;
    toolbar.edgeInsets = NSEdgeInsetsMake(8, 12, 8, 12);
    toolbar.translatesAutoresizingMaskIntoConstraints = NO;

    NSButton *lineButton = [self buttonWithTitle:@"直线" action:@selector(chooseLine:)];
    NSButton *circleButton = [self buttonWithTitle:@"圆" action:@selector(chooseCircle:)];
    NSButton *rectButton = [self buttonWithTitle:@"矩形" action:@selector(chooseRectangle:)];
    NSButton *triangleButton = [self buttonWithTitle:@"三角形" action:@selector(chooseTriangle:)];
    NSButton *clearButton = [self buttonWithTitle:@"清空" action:@selector(clearCanvas:)];
    NSButton *saveButton = [self buttonWithTitle:@"保存" action:@selector(saveCanvas:)];

    self.toolButtons = [NSMutableArray arrayWithObjects:lineButton, circleButton, rectButton, triangleButton, nil];
    [self selectButton:lineButton];

    [toolbar addArrangedSubview:lineButton];
    [toolbar addArrangedSubview:circleButton];
    [toolbar addArrangedSubview:rectButton];
    [toolbar addArrangedSubview:triangleButton];
    [toolbar addArrangedSubview:clearButton];
    [toolbar addArrangedSubview:saveButton];

    self.drawingView = [[DrawingView alloc] initWithFrame:NSMakeRect(0, 0, 980, 660)];
    self.drawingView.translatesAutoresizingMaskIntoConstraints = NO;

    [content addSubview:toolbar];
    [content addSubview:self.drawingView];

    [NSLayoutConstraint activateConstraints:@[
        [toolbar.topAnchor constraintEqualToAnchor:content.topAnchor],
        [toolbar.leadingAnchor constraintEqualToAnchor:content.leadingAnchor],
        [toolbar.trailingAnchor constraintEqualToAnchor:content.trailingAnchor],
        [toolbar.heightAnchor constraintEqualToConstant:48],

        [self.drawingView.topAnchor constraintEqualToAnchor:toolbar.bottomAnchor],
        [self.drawingView.leadingAnchor constraintEqualToAnchor:content.leadingAnchor],
        [self.drawingView.trailingAnchor constraintEqualToAnchor:content.trailingAnchor],
        [self.drawingView.bottomAnchor constraintEqualToAnchor:content.bottomAnchor]
    ]];

    [self.window center];
    [self.window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];
}

- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender {
    return YES;
}

@end

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        NSApplication *app = [NSApplication sharedApplication];
        [app setActivationPolicy:NSApplicationActivationPolicyRegular];
        AppDelegate *delegate = [[AppDelegate alloc] init];
        app.delegate = delegate;
        [app run];
    }

    return 0;
}
