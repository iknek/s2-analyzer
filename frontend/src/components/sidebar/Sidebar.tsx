import { useState, useEffect, useRef } from "react";
import {parser} from "../../parser/Parser.ts";

const [minWidth, maxWidth, defaultWidth] = [200, window.innerWidth/2, window.innerWidth/4];

function Sidebar() {
  const [width, setWidth] = useState(defaultWidth);
  const isResized = useRef(false);

  useEffect(() => {
    window.addEventListener("mousemove", (e) => {
      if (!isResized.current) {
        return;
      }

      setWidth((previousWidth) => {
        const newWidth = previousWidth + e.movementX / 3;

        const isWidthInRange = newWidth >= minWidth && newWidth <= maxWidth;

        return isWidthInRange ? newWidth : previousWidth;
      });
    });

    window.addEventListener("mouseup", () => {
      isResized.current = false;
    });
  }, []);

  return (
      <div className="overflow-auto flex absolute transition-colors">

        <div style={{width: `${width / 16}rem`, height: window.innerHeight*0.86}} className="border-tno-blue border-r bg-base-gray">
            <h1 className={"text-lg text-white"}>All errors:</h1>
            {parser.getErrors().length!=0 && parser.getErrors().map((s:string)=>{
                return (
                <pre className={"text-white overflow-auto bg-base-gray"} style={{maxWidth: width}}>
                    {s}
                </pre>);
            })}
            {parser.getErrors().length==0 && <pre className={"text-white"}>None.</pre>}
        </div>

        <div
            className="w-2 cursor-col-resize"
            onMouseDown={() => {
              isResized.current = true;
            }}
        />
      </div>
  );
}

export default Sidebar;