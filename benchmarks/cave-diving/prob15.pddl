;; Cave Diving STRIPS
;; Authors: Nathan Robinson,
;;          Christian Muise, and
;;          Charles Gretton

(define (problem cave-diving-strips-prob15)
  (:domain cave-diving-strips)
  (:objects
    l0 l1 l2 l3 - location
    t0 t1 dummy - tank
    zero one two three four - quantity
  )

  (:init
    (available d0)
    (available d1)
    (available d2)
    (available d3)
    (capacity d0 four)
    (capacity d1 four)
    (capacity d2 four)
    (capacity d3 four)
    (in-storage t0)
    (next-tank t0 t1)
    (next-tank t1 dummy)
    (cave-entrance l0)
    (connected l0 l1)
    (connected l1 l0)
    (connected l1 l2)
    (connected l2 l1)
    (connected l2 l3)
    (connected l3 l2)
    (next-quantity zero one)
    (next-quantity one two)
    (next-quantity two three)
    (next-quantity three four)
  )

  (:goal
    (and
      (have-photo l3)
      (decompressing d2)
      (decompressing d3)
      (decompressing d0)
      (decompressing d1)
    )
  )

)
