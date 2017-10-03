# Lab2
By: Dan Youngblut and Nick Nordlund

The code is very well documented. We will give brief descriptions, but focus on problems that arose and how we solved them.
### MContainer.c
Find real quota by looping through all pages given by nps,and incremented if passed permision and not allocated.
Various lookup and return functions.
This implementation went smoothly.

### MPTIntro.c 
The identity functions gave us quite a bit of confusion at the start, but eventually we got them. When we wished to set the page directory entry to identity, we must lookup the value of the corresponding page directory index in the `IDTbl`. A page directory entry is the address of a page table. Since page tables are four kilobytes, the last four bits should be zero. Since the identity table is a 2d array, corresponding to page directories and page tables, `IDTbl[pde_index]` will be the address of the `pde_index`th page directory. We need only `OR` this address with the permissions.

`get_pdir_entry` gave us a lot of trouble. The trick we came up with was to treat the table as if it was already allocated. The page directory entry points at the physical address of the first entry of correct table to look in. Now, we have to add to this entry the page table index. The value at that address is the correct page table entry. The page table index has to be  shift left by 2 because it is a 10 bit number that must be used to index into a 12 bit number worth of addresses. Since 12 bits are used to index into a 4 kilobyte table, each byte is addressable. We only care about word addressable which is why we shift by 2.

`set_ptble_entry_identity` we figured it should just be the physical address with the correct permissions

### MPTOp.c
This layer was all about extracting the correct bits to use and plugging them into the funtions created in the intro layer. The `idptbl_init` function initializes the containers. Then loops through the all possible `pde_index` and `pte_index` with a two deep for loop. Setting the identity table with the proper permissions based on whether it is kernel or not.

### MPTComm.c
`pdir_init` intializes the identity table and then has an outer for loop and three inner for loops. The outer loop goes through all the process ids. The inner loops go through the various sections of the memory. Setting the page directory entries to identity for those indeces that are within the kernel space, and removing (set to 0) those that are in the user space.

`alloc_ptbl` recieves a physical address returned by `container_alloc()`. It checks if there is an available page for the page table and then sets the page directory entry by the virtual address to the physcal address of the page table. It then loops through every physical address included in this page and sets them to 0.

`free_ptbl` was waaayyyy easier.

### MPTKern.c
`pdir_init` for process 0 sets the pdir_entry_identity for the user space.

`map_page` gets the address of the page table, checks to see if it is mapped. If not it calls `alloc_ptbl()`. Now that the page table is definitely allocated it sets the page table entry by virtual address to the page index arguement.

### MPTNew.c
`alloc_page` it allocates the pysical page in memory and runs `map_page()` with this page index.
