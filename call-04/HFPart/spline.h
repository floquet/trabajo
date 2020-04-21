#define RELAXED 1
#define CLAMPED 2

#define FIRST_POINT     1
#define LAST_POINT    999

#define ONE_DIMENSION   1
#define TWO_DIMENSION   2
#define THREE_DIMENSION 3

struct spline_element_t {
   double xdata;
   double ydata;
   double zdata;
   double delta_x;
   double delta_y;
   double delta_z;
   double cordlen;              /* L elements */
   double tanvector[3];         /* U elements */
   double pdotvector[3];
   double p2dotvector[3];
   double ndata[4];             /* M elements in a tri-diagonal a,b,c */
   double bdata[3];             /* B elements */
   };

