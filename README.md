# Renault_Project
## By: Sagar Tikmani
## MSc Business Analytics Post-graduate Student
## This repository contains files for the Renault Empty Packaging Dispatching and Routing Problem. 

### Problem Description:
#### Suppliers deliver parts to plants with full packaging. The plants must then return empty packaging to suppliers who need them, ideally to the nearest suppliers. 30 types of standard packaging are shared among all the suppliers.
#### Over a horizon of several weeks split into days, the objective is to dispatch empty packaging from plants to suppliers, in order to avoid shortages of packaging at the suppliers while minimizing km. But the goal is also to find and use the maximum stable routes for these dispatches. A stable route is defined by a plant as a source, a set of maximum 3 suppliers as destinations, and must be used at least once a week, over all the weeks of the horizon. The distance between 2 suppliers of a route should not exceed 200 km.
#### A route can be used several times a week. But a route is used only when it is well filled enough, usually 9 linear meters (mL) for local French routes, 6 mL for local Spanish routes and 11 mL for all the other routes. When there is no route between a plant and a supplier, or when the  route is not well filled enough, the dispatch must use dynamic trucks which cost more than trucks associated with stable routes.
#### Each type of packaging is associated with a linear meter. It represents the place occupied by the packaging in the truck. Trucks have 13.4 linear meters. Packaging can be dispatched only by stacks, not one by one.

