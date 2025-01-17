'use client'; // Required if you ever add interactivity (onClick, etc.)


import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between px-4 py-3 bg-gray-50">
      {/* Left side */}
      <div className='flex flex-1 justify-center items-center max-sm:hidden'>
                {['Our Work', 'About Us'].map((nav,i) => 
                    (<Link href='#' key={nav} className='px-7 text-sm cursor-pointer text-gray-600 hover:text-black transition-all'>
                        {nav}
                    </Link>))}
                    <h1 className="z-10 px-20 text-2xl font-bold">HENNETH</h1>
                    {['Testimonials', 'Future Goals'].map((nav,i) => 
                    (<Link href='#' key={nav} className='px-7 text-sm cursor-pointer items-center text-gray-600 hover:text-black transition-all'>
                        {nav}
                    </Link>))}

            </div>
    </nav>
  );
}
