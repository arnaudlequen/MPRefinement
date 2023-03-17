(define (problem transport-city-sequential-13nodes-1000size-2degree-100mindistance-2trucks-6packages-2012seed)
(:domain transport)
(:objects
capacity-0 capacity-1 capacity-2 capacity-3 capacity-4  - capacity-number
pnum1 pnum2 pnum0  - pnum
city-loc-1 city-loc-2 city-loc-3 city-loc-4 city-loc-5 city-loc-6 city-loc-7 city-loc-8 city-loc-9 city-loc-10 city-loc-11 city-loc-12 city-loc-13  - location
package-bag1 package-bag2 package-bag3 package-bag4 package-bag5  - package
truck-1 truck-2  - vehicle
)
(:init (road city-loc-13 city-loc-11)
(road city-loc-12 city-loc-8)
(road city-loc-4 city-loc-2)
(road city-loc-3 city-loc-1)
(road city-loc-2 city-loc-4)
(road city-loc-13 city-loc-9)
(capacity truck-2 capacity-3)
(road city-loc-5 city-loc-11)
(road city-loc-1 city-loc-3)
(road city-loc-8 city-loc-7)
(road city-loc-5 city-loc-3)
(road city-loc-12 city-loc-2)
(road city-loc-12 city-loc-9)
(road city-loc-7 city-loc-9)
(road city-loc-6 city-loc-13)
(road city-loc-13 city-loc-12)
(road city-loc-9 city-loc-12)
(at-vehicle truck-1 city-loc-1)
(road city-loc-8 city-loc-9)
(road city-loc-13 city-loc-8)
(road city-loc-5 city-loc-1)
(road city-loc-10 city-loc-9)
(road city-loc-10 city-loc-6)
(road city-loc-8 city-loc-6)
(capacity truck-1 capacity-3)
(road city-loc-7 city-loc-6)
(road city-loc-6 city-loc-7)
(road city-loc-3 city-loc-5)
(road city-loc-7 city-loc-8)
(capacity-predecessor capacity-2 capacity-3)
(road city-loc-9 city-loc-13)
(capacity-predecessor capacity-1 capacity-2)
(road city-loc-8 city-loc-12)
(road city-loc-6 city-loc-9)
(road city-loc-11 city-loc-3)
(road city-loc-12 city-loc-13)
(road city-loc-11 city-loc-5)
(road city-loc-9 city-loc-6)
(road city-loc-13 city-loc-6)
(road city-loc-1 city-loc-5)
(road city-loc-11 city-loc-13)
(road city-loc-8 city-loc-13)
(at-vehicle truck-2 city-loc-5)
(road city-loc-6 city-loc-8)
(capacity-predecessor capacity-3 capacity-4)
(road city-loc-9 city-loc-8)
(road city-loc-3 city-loc-11)
(road city-loc-12 city-loc-7)
(road city-loc-7 city-loc-12)
(road city-loc-6 city-loc-10)
(road city-loc-9 city-loc-7)
(road city-loc-2 city-loc-12)
(capacity-predecessor capacity-0 capacity-1)
(road city-loc-9 city-loc-10)
(package-less pnum1 pnum2)
(= (total-cost ) 0)
(= (road-length city-loc-3 city-loc-1) 23)
(= (road-length city-loc-1 city-loc-3) 23)
(= (road-length city-loc-4 city-loc-2) 17)
(= (road-length city-loc-2 city-loc-4) 17)
(= (road-length city-loc-5 city-loc-1) 18)
(= (road-length city-loc-1 city-loc-5) 18)
(= (road-length city-loc-5 city-loc-3) 12)
(= (road-length city-loc-3 city-loc-5) 12)
(= (road-length city-loc-7 city-loc-6) 20)
(= (road-length city-loc-6 city-loc-7) 20)
(= (road-length city-loc-8 city-loc-6) 17)
(= (road-length city-loc-6 city-loc-8) 17)
(= (road-length city-loc-8 city-loc-7) 15)
(= (road-length city-loc-7 city-loc-8) 15)
(= (road-length city-loc-9 city-loc-6) 12)
(= (road-length city-loc-6 city-loc-9) 12)
(= (road-length city-loc-9 city-loc-7) 23)
(= (road-length city-loc-7 city-loc-9) 23)
(= (road-length city-loc-9 city-loc-8) 12)
(= (road-length city-loc-8 city-loc-9) 12)
(= (road-length city-loc-10 city-loc-6) 14)
(= (road-length city-loc-6 city-loc-10) 14)
(= (road-length city-loc-10 city-loc-9) 19)
(= (road-length city-loc-9 city-loc-10) 19)
(= (road-length city-loc-11 city-loc-3) 24)
(= (road-length city-loc-3 city-loc-11) 24)
(= (road-length city-loc-11 city-loc-5) 19)
(= (road-length city-loc-5 city-loc-11) 19)
(= (road-length city-loc-12 city-loc-2) 17)
(= (road-length city-loc-2 city-loc-12) 17)
(= (road-length city-loc-12 city-loc-7) 21)
(= (road-length city-loc-7 city-loc-12) 21)
(= (road-length city-loc-12 city-loc-8) 12)
(= (road-length city-loc-8 city-loc-12) 12)
(= (road-length city-loc-12 city-loc-9) 22)
(= (road-length city-loc-9 city-loc-12) 22)
(= (road-length city-loc-13 city-loc-6) 25)
(= (road-length city-loc-6 city-loc-13) 25)
(= (road-length city-loc-13 city-loc-8) 17)
(= (road-length city-loc-8 city-loc-13) 17)
(= (road-length city-loc-13 city-loc-9) 14)
(= (road-length city-loc-9 city-loc-13) 14)
(= (road-length city-loc-13 city-loc-11) 16)
(= (road-length city-loc-11 city-loc-13) 16)
(= (road-length city-loc-13 city-loc-12) 19)
(= (road-length city-loc-12 city-loc-13) 19)
(count-package package-bag1 city-loc-7 pnum0)
(count-package package-bag1 city-loc-8 pnum1)
(count-package package-bag2 city-loc-1 pnum1)
(count-package package-bag3 city-loc-6 pnum1)
(count-package package-bag4 city-loc-11 pnum1)
(count-package package-bag5 city-loc-4 pnum1)
(package-less pnum0 pnum1)
(count-package package-bag1 city-loc-1 pnum0)
(count-package package-bag1 city-loc-2 pnum0)
(count-package package-bag1 city-loc-3 pnum0)
(count-package package-bag1 city-loc-4 pnum0)
(count-package package-bag1 city-loc-5 pnum0)
(count-package package-bag1 city-loc-6 pnum0)
(count-package package-bag1 city-loc-9 pnum0)
(count-package package-bag1 city-loc-10 pnum0)
(count-package package-bag1 city-loc-11 pnum0)
(count-package package-bag1 city-loc-12 pnum0)
(count-package package-bag1 city-loc-13 pnum0)
(count-package package-bag1 truck-1 pnum0)
(count-package package-bag1 truck-2 pnum0)
(count-package package-bag2 city-loc-2 pnum0)
(count-package package-bag2 city-loc-3 pnum0)
(count-package package-bag2 city-loc-4 pnum0)
(count-package package-bag2 city-loc-5 pnum0)
(count-package package-bag2 city-loc-6 pnum0)
(count-package package-bag2 city-loc-7 pnum0)
(count-package package-bag2 city-loc-8 pnum0)
(count-package package-bag2 city-loc-9 pnum0)
(count-package package-bag2 city-loc-10 pnum0)
(count-package package-bag2 city-loc-11 pnum0)
(count-package package-bag2 city-loc-12 pnum0)
(count-package package-bag2 city-loc-13 pnum0)
(count-package package-bag2 truck-1 pnum0)
(count-package package-bag2 truck-2 pnum0)
(count-package package-bag3 city-loc-1 pnum0)
(count-package package-bag3 city-loc-2 pnum0)
(count-package package-bag3 city-loc-3 pnum0)
(count-package package-bag3 city-loc-4 pnum0)
(count-package package-bag3 city-loc-5 pnum0)
(count-package package-bag3 city-loc-7 pnum0)
(count-package package-bag3 city-loc-8 pnum0)
(count-package package-bag3 city-loc-9 pnum0)
(count-package package-bag3 city-loc-10 pnum0)
(count-package package-bag3 city-loc-11 pnum0)
(count-package package-bag3 city-loc-12 pnum0)
(count-package package-bag3 city-loc-13 pnum0)
(count-package package-bag3 truck-1 pnum0)
(count-package package-bag3 truck-2 pnum0)
(count-package package-bag4 city-loc-1 pnum0)
(count-package package-bag4 city-loc-2 pnum0)
(count-package package-bag4 city-loc-3 pnum0)
(count-package package-bag4 city-loc-4 pnum0)
(count-package package-bag4 city-loc-5 pnum0)
(count-package package-bag4 city-loc-6 pnum0)
(count-package package-bag4 city-loc-7 pnum0)
(count-package package-bag4 city-loc-8 pnum0)
(count-package package-bag4 city-loc-9 pnum0)
(count-package package-bag4 city-loc-10 pnum0)
(count-package package-bag4 city-loc-12 pnum0)
(count-package package-bag4 city-loc-13 pnum0)
(count-package package-bag4 truck-1 pnum0)
(count-package package-bag4 truck-2 pnum0)
(count-package package-bag5 city-loc-1 pnum0)
(count-package package-bag5 city-loc-2 pnum0)
(count-package package-bag5 city-loc-3 pnum0)
(count-package package-bag5 city-loc-5 pnum0)
(count-package package-bag5 city-loc-6 pnum0)
(count-package package-bag5 city-loc-7 pnum0)
(count-package package-bag5 city-loc-8 pnum0)
(count-package package-bag5 city-loc-9 pnum0)
(count-package package-bag5 city-loc-10 pnum0)
(count-package package-bag5 city-loc-11 pnum0)
(count-package package-bag5 city-loc-12 pnum0)
(count-package package-bag5 city-loc-13 pnum0)
(count-package package-bag5 truck-1 pnum0)
(count-package package-bag5 truck-2 pnum0)
(package-bag-size package-bag1 pnum2)
(package-bag-size package-bag2 pnum1)
(package-bag-size package-bag3 pnum1)
(package-bag-size package-bag4 pnum1)
(package-bag-size package-bag5 pnum1)
(package-lte-sum pnum0 pnum0 pnum2)
(package-lte-sum pnum0 pnum1 pnum2)
(package-lte-sum pnum0 pnum2 pnum2)
(package-lte-sum pnum1 pnum0 pnum2)
(package-lte-sum pnum1 pnum1 pnum2)
(package-lte-sum pnum2 pnum0 pnum2)
(package-lte-sum pnum0 pnum0 pnum1)
(package-lte-sum pnum0 pnum1 pnum1)
(package-lte-sum pnum1 pnum0 pnum1)
)
(:goal (and
	  (count-package package-bag1 city-loc-4 pnum2)
	  (count-package package-bag2 city-loc-3 pnum1)
	  (count-package package-bag3 city-loc-8 pnum1)
	  (count-package package-bag4 city-loc-6 pnum1)
	  (count-package package-bag5 city-loc-1 pnum1))
)
(:metric minimize (total-cost))
)
