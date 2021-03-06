Point(1) = {0.0, 0.0, 0.0}; // back lower left
Point(2) = {2.5, 0.0, 0.0}; // back lower right
Point(3) = {2.5, 0.41, 0.0}; // back upper right
Point(4) = {0.0, 0.41, 0.0}; // back upper left
Point(5) = {0.0, 0.0, 0.41}; // front lower left
Point(6) = {2.5, 0.0, 0.41}; // front lower right
Point(7) = {2.5, 0.41, 0.41}; // front upper right
Point(8) = {0.0, 0.41, 0.41}; // front upper left
Line(1) = {1, 2}; // back bottom
Line(2) = {2, 3}; // back right
Line(3) = {3, 4}; // back top
Line(4) = {4, 1}; // back left
Line(5) = {5, 6}; // front bottom
Line(6) = {6, 7}; // front right
Line(7) = {7, 8}; // front top
Line(8) = {8, 5}; // front left
Line(9) = {1, 5}; // back-front bottom left
Line(10) = {2, 6}; // back-front bottom right
Line(11) = {3, 7}; // back-front top right
Line(12) = {4, 8}; // back-front top left
Line Loop(1) = {1, 2, 3, 4}; // back
Line Loop(2) = {5, 6, 7, 8}; // front
Line Loop(3) = {12, 8, -9, -4}; // left
Plane Surface(1) = {3}; // left
Line Loop(4) = {2, 11, -6, -10}; // right
Plane Surface(2) = {4}; // right
Line Loop(5) = {3, 12, -7, -11}; // top
Plane Surface(3) = {5}; // top
Line Loop(6) = {1, 10, -5, -9}; // bottom
Plane Surface(4) = {6}; // bottom

Point(9) = {0.5, 0.2, 0.0}; // back circle center
Point(10) = {0.45, 0.2, 0.0}; // back circle left
Point(11) = {0.5, 0.15, 0.0}; // back circle bottom
Point(12) = {0.55, 0.2, 0.0}; // back circle right
Point(13) = {0.5, 0.25, 0.0}; // back circle top
Circle(13) = {10, 9, 11}; // back left bottom
Circle(14) = {11, 9, 12}; // back right bottom
Circle(15) = {12, 9, 13}; // back right top
Circle(16) = {13, 9, 10}; // back left top
Line Loop(7) = { 13, 14, 15, 16 }; // back circle
Plane Surface(5) = { 1, 7 }; // back without circle
Point(14) = {0.5, 0.2, 0.41}; // front circle center
Point(15) = {0.45, 0.2, 0.41}; // front circle left
Point(16) = {0.5, 0.15, 0.41}; // front circle bottom
Point(17) = {0.55, 0.2, 0.41}; // front circle right
Point(18) = {0.5, 0.25, 0.41}; // front circle top
Circle(17) = {15, 14, 16}; // front left bottom
Circle(18) = {16, 14, 17}; // front right bottom
Circle(19) = {17, 14, 18}; // front right top
Circle(20) = {18, 14, 15}; // front left top
Line Loop(8) = { 17, 18, 19, 20 }; // back circle
Plane Surface(6) = { 2, 8 }; // front without circle
Line(21) = {10, 15}; // back-front left
Line(22) = {11, 16}; // back-front left
Line(23) = {12, 17}; // back-front left
Line(24) = {13, 18}; // back-front left

Line Loop(9) = {21, -20, -24, 16}; 
Ruled Surface(7) = {9}; 

Line Loop(10) = {24, -19, -23, 15}; 
Ruled Surface(8) = {10}; 

Line Loop(11) = {23, -18, -22, 14}; 
Ruled Surface(9) = {11}; 

Line Loop(12) = {22, -17, -21, 13}; 
Ruled Surface(10) = {12}; 

Surface Loop(1) = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
Volume(1) = {1};
