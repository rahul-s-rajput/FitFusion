import * as React from "react"

import { cn } from "../../lib/utils"

type Orientation = "horizontal" | "vertical"

interface SeparatorProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: Orientation
  decorative?: boolean
}

const Separator = React.forwardRef<HTMLDivElement, SeparatorProps>(
  ({ className, orientation = "horizontal", decorative = true, ...props }, ref) => {
    const orientationClass =
      orientation === "vertical" ? "h-full w-px" : "h-px w-full"

    return (
      <div
        ref={ref}
        role={decorative ? "presentation" : "separator"}
        aria-orientation={orientation}
        className={cn("shrink-0 bg-border", orientationClass, className)}
        {...props}
      />
    )
  }
)
Separator.displayName = "Separator"

export { Separator }